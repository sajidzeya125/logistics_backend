from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# jwt token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None    


# user schemas
class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
# driver schemas
class DriverCreate(BaseModel):
    name: str
    license_number: str


class DriverOut(BaseModel):
    id: int
    user_id: int
    name: str
    license_number: str
    is_available: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



# logistics/gps schemas
class LocationUpdate(BaseModel):
    latitude: float
    longitude: float