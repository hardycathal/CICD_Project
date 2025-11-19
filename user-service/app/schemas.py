from typing import Annotated, Optional, List
from annotated_types import Ge, Le
from pydantic import BaseModel, EmailStr, ConfigDict, StringConstraints


NameStr        = Annotated[str, StringConstraints(min_length=1, max_length=50)] 
PasswordStr = Annotated[str, StringConstraints(min_length=8, max_length=50)]

class UserCreate(BaseModel):
    username: NameStr
    email: EmailStr
    password: PasswordStr

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: NameStr
    email: EmailStr
    password: PasswordStr

class UserLogin(BaseModel):
    username_or_email: str
    passsword: PasswordStr

