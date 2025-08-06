from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, field_validator
import logging

from ..models.database import get_db, User
from ..services.auth_service import (
    verify_password, get_password_hash, create_access_token,
    verify_token, ACCESS_TOKEN_EXPIRE_MINUTES, validate_password
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class UserCreate(BaseModel):
    username: str
    password: str
    
    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v
    
    @field_validator('password')
    @classmethod
    def password_must_be_valid(cls, v):
        if not validate_password(v):
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=dict)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user registered: {user.username}")
        return {"message": "User created successfully", "user_id": db_user.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: str = Depends(lambda token=Depends(oauth2_scheme): verify_token(token)),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at.isoformat(),
        is_active=bool(user.is_active)
    )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)
