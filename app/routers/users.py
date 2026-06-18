from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app import auth2, models
from app.crud.user_crud import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = crud.user_crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    db_user = crud.user_crud.create_user(db, user)
    return db_user


@router.get("/me", response_model=schemas.UserOut)
def get_current_user_profile(
    current_user = Depends(auth2.get_current_user)
):
    """Get current logged-in user's profile"""
    return current_user


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get user by ID"""
    db_user = crud.user_crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.get("/", response_model=list[schemas.UserOut])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get all users (admin only - can be restricted later)"""
    return crud.user_crud.get_all_users(db, skip=skip, limit=limit)


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_update: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Update user details"""
    # Only allow users to update their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    db_user = crud.user_crud.update_user(
        db,
        user_id,
        email=user_update.email
    )
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Delete a user"""
    # Only allow users to delete their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    success = crud.user_crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


# ==================== Driver Routes ====================

@router.post("/drivers/profile", response_model=schemas.DriverOut, status_code=status.HTTP_201_CREATED)
def create_driver_profile(
    driver: schemas.DriverCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Create driver profile for current user"""
    existing_driver = crud.user_crud.get_driver_by_user(db, current_user.id)
    if existing_driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver profile already exists for this user"
        )
    
    db_driver = crud.user_crud.create_driver_profile(db, current_user.id, driver)
    return db_driver


@router.get("/drivers/me", response_model=schemas.DriverOut)
def get_my_driver_profile(
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get current user's driver profile"""
    db_driver = crud.user_crud.get_driver_by_user(db, current_user.id)
    if not db_driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No driver profile found"
        )
    return db_driver


@router.get("/drivers/", response_model=list[schemas.DriverOut])
def get_all_drivers(
    available_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get all drivers"""
    return crud.user_crud.get_all_drivers(
        db,
        available_only=available_only,
        skip=skip,
        limit=limit
    )


@router.patch("/drivers/{driver_id}/availability")
def update_driver_availability(
    driver_id: int,
    is_available: bool = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Update driver availability status"""
    # Get driver to check if it belongs to current user or if user is admin
    db_driver = db.query(models.Driver).filter(
        models.Driver.id == driver_id
    ).first()
    
    if not db_driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Only allow drivers to update their own status
    if db_driver.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own availability"
        )
    
    updated_driver = crud.user_crud.update_driver_availability(
        db,
        driver_id,
        is_available
    )
    
    return updated_driver