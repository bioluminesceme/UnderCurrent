from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.database import get_db
from backend.models import User
import bcrypt

router = APIRouter()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    age: Optional[int] = None
    sex: Optional[str] = None
    bmi: Optional[float] = None

class UserResponse(BaseModel):
    id: int
    email: str
    age: Optional[int]
    sex: Optional[str]
    bmi: Optional[float]
    created_at: str

    class Config:
        from_attributes = True
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }

    @classmethod
    def model_validate(cls, obj):
        """Custom validation to convert datetime to string"""
        if hasattr(obj, 'created_at') and obj.created_at:
            obj_dict = {
                'id': obj.id,
                'email': obj.email,
                'age': obj.age,
                'sex': obj.sex,
                'bmi': obj.bmi,
                'created_at': obj.created_at.isoformat()
            }
            return cls(**obj_dict)
        return super().model_validate(obj)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Create user
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        age=user.age,
        sex=user.sex,
        bmi=user.bmi
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse.model_validate(db_user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)
