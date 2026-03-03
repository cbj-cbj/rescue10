from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 用户
class UserCreate(BaseModel):
    username: str
    password: str
    real_name: str
    student_id: str
    phone: Optional[str] = None
class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    created_at: datetime
    class Config: from_attributes = True
class LoginRequest(BaseModel):
    username: str
    password: str

# 动物
class AnimalBase(BaseModel):
    name: str
    breed: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    health_status: Optional[str] = None
    vaccine_status: Optional[str] = None
    personality: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = "待领养"
class AnimalCreate(AnimalBase): pass
class AnimalResponse(AnimalBase):
    id: int
    created_at: Optional[datetime] = None
    class Config: from_attributes = True
class AnimalStatusUpdate(BaseModel):
    status: str

# 领养 (含学院班级)
class AdoptionCreate(BaseModel):
    user_id: int
    animal_id: int
    college: str
    student_class: str
    apply_reason: str
class AdoptionAudit(BaseModel):
    status: str
    admin_comment: Optional[str] = None
class AdoptionResponse(BaseModel):
    id: int
    user_id: int
    animal_id: int
    college: str
    student_class: str
    apply_reason: str
    status: str
    admin_comment: Optional[str] = None
    apply_date: datetime
    class Config: from_attributes = True

# 捐赠
class DonationCreate(BaseModel):
    user_id: int
    item_name: str
    quantity: str
    remarks: Optional[str] = None
class DonationResponse(BaseModel):
    id: int
    user_id: int
    item_name: str
    quantity: str
    remarks: Optional[str] = None
    donate_date: datetime
    class Config: from_attributes = True

# 志愿者
class VolunteerCreate(BaseModel):
    user_id: int
    reason: str
    available_time: str
class VolunteerAudit(BaseModel):
    status: str
class VolunteerResponse(BaseModel):
    id: int
    user_id: int
    reason: str
    available_time: str
    status: str
    apply_date: datetime
    class Config: from_attributes = True

# 任务
class TaskCreate(BaseModel):
    title: str
    description: str
    required_count: int
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    required_count: int
    status: str
    created_at: datetime
    class Config: from_attributes = True

# --- 寻宠 (这里是你缺失的部分) ---
class LostPetCreate(BaseModel):
    title: str
    type: str 
    description: str
    contact: str

# ✅ 新增：审核模型 (解决报错的关键)
class LostPetAudit(BaseModel):
    status: str

class LostPetResponse(BaseModel):
    id: int
    title: str
    type: str
    description: str
    contact: str
    status: str          # ✅ 修改：增加了 status 字段
    created_at: datetime
    class Config: from_attributes = True