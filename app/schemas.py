from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    age: int

class UserOut(UserCreate):
    id: int

    class Config:
        orm_mode = True
