from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, auth2, crud
from app.database import get_db
from app.crud.user_crud import verify_password

router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
   
    # Get user by email
    user = crud.user_crud.get_user_by_email(db, user_credentials.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token = auth2.create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    current_user = Depends(auth2.get_current_user)
):
   
    
    return {"message": "Successfully logged out. Please discard your token."}


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(
    current_user = Depends(auth2.get_current_user)
):
    access_token = auth2.create_access_token(data={"sub": current_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify", response_model=schemas.UserOut)
def verify_token(
    current_user = Depends(auth2.get_current_user)
):
   
    return current_user