from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    
    if existing_user:
        return None  # User already exists
    
    # Hash password
    hashed_password = hash_password(user.password)
    
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> models.User:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> models.User:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> list:
    """Get all users with pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user(
    db: Session,
    user_id: int,
    email: str = None,
    is_active: bool = None
) -> models.User:
    """Update user details"""
    db_user = get_user_by_id(db, user_id)
    
    if db_user:
        if email:
            # Check if new email already exists
            existing = db.query(models.User).filter(
                and_(models.User.email == email, models.User.id != user_id)
            ).first()
            if not existing:
                db_user.email = email
        
        if is_active is not None:
            db_user.is_active = is_active
        
        db.commit()
        db.refresh(db_user)
    
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    db_user = get_user_by_id(db, user_id)
    
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    
    return False


def create_driver_profile(
    db: Session,
    user_id: int,
    driver_data: schemas.DriverCreate
) -> models.Driver:
    """Create a driver profile for a user"""
    # Check if driver already exists for this user
    existing_driver = db.query(models.Driver).filter(
        models.Driver.user_id == user_id
    ).first()
    
    if existing_driver:
        return None  # Driver already exists
    
    db_driver = models.Driver(
        user_id=user_id,
        name=driver_data.name,
        license_number=driver_data.license_number,
        is_available=True
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver


def get_driver_by_user(db: Session, user_id: int) -> models.Driver:
    """Get driver profile for a user"""
    return db.query(models.Driver).filter(
        models.Driver.user_id == user_id
    ).first()


def get_all_drivers(db: Session, available_only: bool = False, skip: int = 0, limit: int = 10) -> list:
    """Get all drivers"""
    query = db.query(models.Driver)
    
    if available_only:
        query = query.filter(models.Driver.is_available == True)
    
    return query.offset(skip).limit(limit).all()


def update_driver_availability(
    db: Session,
    driver_id: int,
    is_available: bool
) -> models.Driver:
    """Update driver availability status"""
    db_driver = db.query(models.Driver).filter(
        models.Driver.id == driver_id
    ).first()
    
    if db_driver:
        db_driver.is_available = is_available
        db_driver.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_driver)
    
    return db_driver