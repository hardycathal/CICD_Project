from fastapi import FastAPI, Depends, HTTPException, status, Response 
from contextlib import asynccontextmanager 
from sqlalchemy.orm import Session 
from sqlalchemy import select 
from sqlalchemy.exc import IntegrityError 
from sqlalchemy.orm import selectinload 
from fastapi.middleware.cors import CORSMiddleware 
from .database import engine, SessionLocal, get_db
from .models import Base, UserDB
from .schemas import ( 
    UserCreate, UserRead,
    UserLogin
) 

#Replacing @app.on_event("startup") 
@asynccontextmanager 
async def lifespan(app: FastAPI): 
    Base.metadata.create_all(bind=engine)    
    yield 

app = FastAPI(lifespan=lifespan)

 
def commit_or_rollback(db: Session, error_msg: str): 
    try: 
        db.commit() 
    except IntegrityError: 
        db.rollback() 
        raise HTTPException(status_code=409, detail=error_msg) 
 

## Health Check ##
@app.get("/health") 
def health(): 
    return {"status": "ok"} 
 

## List Users ##
@app.get("/api/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    stmt= select(UserDB).order_by(UserDB.id)
    result = db.execute(stmt)
    users = result.scalars().all()
    return users


## Get User by ID ##
@app.get("/api/users/{user_id}", response_model=UserRead) 
def get_user(user_id: int, db: Session = Depends(get_db)): 
    user = db.get(UserDB, user_id) 
    if not user: 
        raise HTTPException(status_code=404, detail="User not found") 
    return user 

## Create/Register User ##
@app.post("/api/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED) 
def register(payload: UserCreate, db: Session = Depends(get_db)): 
    user = UserDB(**payload.model_dump()) 
    db.add(user) 
    try: 
        db.commit() 
        db.refresh(user) 
    except IntegrityError: 
        db.rollback() 
        raise HTTPException(status_code=409, detail="User already exists") 
    return user 

## Login ##
@app.post("/api/users/login", response_model=UserRead)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    stmt = select(UserDB).where(UserDB.username == payload.username_or_email)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        stmt = select(UserDB).where(UserDB.email == payload.username_or_email)
        user = db.execute(stmt).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return user

# DELETE a user (triggers ORM cascade -> deletes their projects too) 
@app.delete("/api/users/{user_id}", status_code=204) 
def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response: 
    user = db.get(UserDB, user_id) 
    if not user: 
        raise HTTPException(status_code=404, detail="User not found") 
    db.delete(user)          # <-- triggers cascade="all, delete-orphan" on projects 
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)