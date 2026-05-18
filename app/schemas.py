from pydantic import BaseModel, ConfigDict, Field
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


# Location schemas
class LocationBase(BaseModel):
    latitude: float
    longitude: float
    address: str
    city: str
    postal_code: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# order item schemas
class OrderItemCreate(BaseModel):
    product_name: str
    quantity: int = Field(..., gt=0)
    weight: Optional[float] = None
    dimensions: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    order_id: int
    product_name: str
    quantity: int 
    weight: Optional[float]
    dimensions: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)    


# order schemas
class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    delivery_location_id: int
    special_instructions: Optional[str] = None
    items: list[OrderItemCreate]


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    special_instructions: Optional[str] = None
    status: Optional[str] = None    


class OrderOut(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    customer_phone: str
    delivery_location_id: int
    status: str
    special_instructions: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut] = []

    model_config = ConfigDict(from_attributes=True)

class OrderListOut(BaseModel):
    id: int
    customer_name: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  


# rote_stop schemas
class RouteStopCreate(BaseModel):
    order_id: int
    location_id: int
    sequence: int


class RouteStopOut(BaseModel):
    id: int
    route_id: int
    order_id: int
    location_id: int
    sequence: int
    status: str
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



# Route schemas
class RouteCreate(BaseModel):
    driver_id: int
    date: datetime


class RouteOptimize(BaseModel):
    order_ids: list[int] = Field(..., description="List of order IDs to optimize the route for") 


class RouteOut(BaseModel):
    id: int
    driver_id: int
    date: datetime
    status: str
    total_distance: Optional[int] = None
    estimated_time: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    stops: list[RouteStopOut] = []

    model_config = ConfigDict(from_attributes=True)


class RouteListOut(BaseModel):
    id: int
    driver_id: int
    date: datetime
    status: str
    total_distance: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)       