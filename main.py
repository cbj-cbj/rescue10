import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

from db_config import engine, get_db, Base
import models, schemas

# 自动建表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="校园流浪动物救助系统", version="2.5.0")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# 初始化管理员 (精简版)
def init_admin():
    from db_config import SessionLocal
    db = SessionLocal()
    if not db.query(models.User).filter(models.User.username == "admin").first():
        db.add(models.User(username="admin", password="admin123", real_name="管理员", student_id="0000000000", phone="000", role="admin"))
        db.commit()
    db.close()
init_admin()

# --- 1. 用户模块 ---
@app.post("/users", response_model=schemas.UserResponse, tags=["用户"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.username == "admin": raise HTTPException(400, "禁止注册 admin")
    if len(user.student_id) != 10 or not user.student_id.isdigit(): raise HTTPException(400, "学号须10位数字")
    if user.student_id[:2] not in ["22", "23", "24", "25"]: raise HTTPException(400, "学号须22-25开头")
    if not (1 <= int(user.student_id[-3:]) <= 100): raise HTTPException(400, "学号尾数须001-100")
    if db.query(models.User).filter(models.User.username == user.username).first(): raise HTTPException(400, "用户名已存在")
    if db.query(models.User).filter(models.User.student_id == user.student_id).first(): raise HTTPException(400, "学号已注册")
    new_user = models.User(username=user.username, password=user.password, real_name=user.real_name, student_id=user.student_id, phone=user.phone, role="user")
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.UserResponse, tags=["用户"])
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or user.password != req.password: raise HTTPException(400, "账号或密码错误")
    return user

@app.get("/users", response_model=List[schemas.UserResponse], tags=["用户"])
def get_users(db: Session = Depends(get_db)): return db.query(models.User).all()

@app.delete("/users/{user_id}", tags=["用户"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(404, "用户不存在")
    if user.role == 'admin': raise HTTPException(400, "禁止删除管理员")
    # 级联删除相关数据
    for model in [models.Adoption, models.Donation, models.Volunteer]:
        db.query(model).filter(model.user_id == user_id).delete()
    db.delete(user); db.commit()
    return {"message": "已注销"}

# --- 2. 动物模块 ---
@app.get("/animals", response_model=List[schemas.AnimalResponse])
def get_animals(db: Session = Depends(get_db)): return db.query(models.Animal).all()

@app.get("/animals/detail/{animal_id}", response_model=schemas.AnimalResponse)
def get_animal_detail(animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal: raise HTTPException(404, "未找到该动物档案")
    return animal

@app.post("/animals", response_model=schemas.AnimalResponse)
def create_animal(animal: schemas.AnimalCreate, db: Session = Depends(get_db)):
    a = models.Animal(**animal.dict())
    db.add(a); db.commit(); db.refresh(a)
    return a

@app.put("/animals/{id}/status", response_model=schemas.AnimalResponse)
def update_animal_status(id: int, s: schemas.AnimalStatusUpdate, db: Session = Depends(get_db)):
    a = db.query(models.Animal).filter(models.Animal.id == id).first()
    if not a: raise HTTPException(404, "动物不存在")
    a.status = s.status
    db.commit(); db.refresh(a)
    return a

@app.delete("/animals/{animal_id}")
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal: raise HTTPException(404, "找不到该动物")
    db.query(models.Adoption).filter(models.Adoption.animal_id == animal_id).delete()
    db.delete(animal); db.commit()
    return {"message": "删除成功"}

# --- 3. 领养模块 ---
@app.post("/adoptions", response_model=schemas.AdoptionResponse)
def apply_adoption(app: schemas.AdoptionCreate, db: Session = Depends(get_db)):
    a = db.query(models.Animal).filter(models.Animal.id == app.animal_id).first()
    if not a or a.status != "待领养": raise HTTPException(400, "无法申请")
    new_app = models.Adoption(**app.dict(), status="待审核")
    db.add(new_app); db.commit(); db.refresh(new_app)
    return new_app

@app.get("/adoptions", response_model=List[schemas.AdoptionResponse])
def get_adoptions(db: Session = Depends(get_db)): return db.query(models.Adoption).all()

@app.put("/adoptions/{id}", response_model=schemas.AdoptionResponse)
def audit_adoption(id: int, audit: schemas.AdoptionAudit, db: Session = Depends(get_db)):
    app = db.query(models.Adoption).filter(models.Adoption.id == id).first()
    if not app: raise HTTPException(404)
    app.status = audit.status
    if audit.status == "已通过":
        an = db.query(models.Animal).filter(models.Animal.id == app.animal_id).first()
        if an: an.status = "已领养"
    db.commit(); db.refresh(app)
    return app

@app.delete("/adoptions/{id}")
def del_adoption(id: int, db: Session = Depends(get_db)):
    db.query(models.Adoption).filter(models.Adoption.id == id).delete()
    db.commit(); return {"msg": "deleted"}

# --- 4. 捐赠模块 ---
@app.post("/donations", response_model=schemas.DonationResponse)
def create_donation(d: schemas.DonationCreate, db: Session = Depends(get_db)):
    nd = models.Donation(**d.dict())
    db.add(nd); db.commit(); db.refresh(nd)
    return nd

@app.get("/donations", response_model=List[schemas.DonationResponse])
def get_donations(db: Session = Depends(get_db)): return db.query(models.Donation).all()

@app.delete("/donations/{donation_id}")
def delete_donation(donation_id: int, db: Session = Depends(get_db)):
    d = db.query(models.Donation).filter(models.Donation.id == donation_id).first()
    if not d: raise HTTPException(404, "无此记录")
    db.delete(d); db.commit(); return {"message": "删除成功"}

# --- 5. 志愿者 ---
@app.post("/volunteers", response_model=schemas.VolunteerResponse)
def apply_vol(v: schemas.VolunteerCreate, db: Session = Depends(get_db)):
    nv = models.Volunteer(**v.dict(), status="待审核")
    db.add(nv); db.commit(); db.refresh(nv)
    return nv

@app.get("/volunteers", response_model=List[schemas.VolunteerResponse])
def get_vols(db: Session = Depends(get_db)): return db.query(models.Volunteer).all()

@app.put("/volunteers/{id}", response_model=schemas.VolunteerResponse)
def audit_vol(id: int, audit: schemas.VolunteerAudit, db: Session = Depends(get_db)):
    v = db.query(models.Volunteer).filter(models.Volunteer.id == id).first()
    if v: v.status = audit.status; db.commit(); db.refresh(v)
    return v

@app.delete("/volunteers/{id}")
def del_vol(id: int, db: Session = Depends(get_db)):
    db.query(models.Volunteer).filter(models.Volunteer.id == id).delete(); db.commit()
    return {"msg": "deleted"}

# --- 6. 任务 ---
@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(t: schemas.TaskCreate, db: Session = Depends(get_db)):
    nt = models.Task(**t.dict())
    db.add(nt); db.commit(); db.refresh(nt)
    return nt

@app.get("/tasks", response_model=List[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)): return db.query(models.Task).all()

@app.delete("/tasks/{id}")
def del_task(id: int, db: Session = Depends(get_db)):
    db.query(models.Task).filter(models.Task.id == id).delete(); db.commit()
    return {"msg": "deleted"}

# --- 7. 统计 ---
@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "animal_stats": [
            {"name": "待领养", "value": db.query(models.Animal).filter(models.Animal.status=="待领养").count()},
            {"name": "已领养", "value": db.query(models.Animal).filter(models.Animal.status=="已领养").count()}
        ],
        "core_metrics": {
            "total_users": db.query(models.User).count(),
            "total_animals": db.query(models.Animal).count(),
            "total_donations": db.query(models.Donation).count(),
            "total_volunteers": db.query(models.Volunteer).filter(models.Volunteer.status=="已通过").count(),
            "pending_adoptions": db.query(models.Adoption).filter(models.Adoption.status=="待审核").count()
        }
    }

# --- 8. 寻宠 ---
@app.post("/lost-pets", response_model=schemas.LostPetResponse)
def create_lost_pet(p: schemas.LostPetCreate, db: Session = Depends(get_db)):
    np = models.LostPet(**p.dict(), status="待审核")
    db.add(np); db.commit(); db.refresh(np)
    return np

@app.put("/lost-pets/{id}/status", response_model=schemas.LostPetResponse)
def audit_lost_pet(id: int, audit: schemas.LostPetAudit, db: Session = Depends(get_db)):
    p = db.query(models.LostPet).filter(models.LostPet.id == id).first()
    if not p: raise HTTPException(404, "Not found")
    p.status = audit.status
    db.commit(); db.refresh(p)
    return p

@app.get("/lost-pets", response_model=List[schemas.LostPetResponse])
def get_lost_pets(db: Session = Depends(get_db)): return db.query(models.LostPet).all()

@app.delete("/lost-pets/{id}")
def delete_lost_pet(id: int, db: Session = Depends(get_db)):
    db.query(models.LostPet).filter(models.LostPet.id == id).delete(); db.commit()
    return {"msg": "deleted"}

# 挂载静态文件
if not os.path.exists("animals"): os.makedirs("animals")
app.mount("/animals", StaticFiles(directory="animals"), name="animals")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)