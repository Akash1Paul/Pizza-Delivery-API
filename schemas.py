from typing import Optional
from pydantic import BaseModel, EmailStr
class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # For Pydantic v2.x (replaces orm_mode)

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True  # For Pydantic v2.x (replaces orm_mode)



class SignUpModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_staff: bool = False
    is_active: bool = True
    class Config:
        from_attributes = True
        json_schema_extra={
            'example':{
                "username":"johndoe",
                "email":"johndoe@gmail.com",
                "password":"password",
                "is_staff":False,
                "is_active":True
            }
        }  


class Settings(BaseModel):
    authjwt_secret_key:str='284e0b2757c70196beb1b2e570f7beabe0ec3d04af709949aedc7d61bec5a8d1'
    authjwt_algorithm: str = "HS256"             # Default algorithm for signing the JWT
    authjwt_access_token_expires: int = 3600       # Access token expiration time in minutes
    authjwt_refresh_token_expires: int = 30      # Refresh token expiration time in days

class LoginModel(BaseModel):
    username: str
    password: str

class OrderModel(BaseModel):
    quantity : str
    order_status : Optional[str]="PENDING" 
    pizza_size : Optional[str]="SMALL"  
    user_id : Optional[int]

    class Config:
        from_attributes = True 
        schema_extra={
            'example':{
                "quantity":2,
                "pizza_size":"LARGE"
            }
        }  

class OrderStatusModel(BaseModel):
    order_status:Optional[str]="PENDING"

    class Config:
        from_attributes = True 
        schema_extra={
            'example':{
                "order_status":"PENDING",
            }
        }  