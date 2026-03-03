from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from db_config import Base
from datetime import datetime

# 1. 用户表
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    real_name = Column(String)
    student_id = Column(String, unique=True, index=True)
    phone = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.now)

# 2. 动物表
class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    breed = Column(String)
    age = Column(String)
    gender = Column(String)
    health_status = Column(String)
    vaccine_status = Column(String)
    personality = Column(String)
    image_url = Column(String)
    status = Column(String, default="待领养") 
    created_at = Column(DateTime, default=datetime.now)

# 3. 领养申请表
class Adoption(Base):
    __tablename__ = "adoptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    animal_id = Column(Integer, index=True)
    college = Column(String)
    student_class = Column(String)
    apply_reason = Column(String)
    status = Column(String, default="待审核")
    admin_comment = Column(String, nullable=True)
    apply_date = Column(DateTime, default=datetime.now)

# 4. 捐赠记录表
class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    item_name = Column(String)
    quantity = Column(String)
    remarks = Column(String, nullable=True)
    donate_date = Column(DateTime, default=datetime.now)

# 5. 志愿者申请表
class Volunteer(Base):
    __tablename__ = "volunteers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    reason = Column(String)
    available_time = Column(String)
    status = Column(String, default="待审核")
    apply_date = Column(DateTime, default=datetime.now)

# 6. 志愿任务表
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    required_count = Column(Integer)
    status = Column(String, default="招募中")
    created_at = Column(DateTime, default=datetime.now)

# 7. 寻宠启事表
class LostPet(Base):
    __tablename__ = "lost_pets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    type = Column(String) # 寻宠/寻主
    description = Column(String)
    contact = Column(String)
    status = Column(String, default="待审核")  # ✅ 必须有这个字段
    created_at = Column(DateTime, default=datetime.now)