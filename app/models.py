import enum

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, TIMESTAMP, text
from sqlalchemy.orm import relationship
from .database import Base
from geoalchemy2 import Geometry

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    driver_profile = relationship("Driver", back_populates="user", uselist=False)
    

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name= Column(String, nullable=False)
    license_number = Column(String, unique=True, index=True, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=text('now()'))

    # Relationship with User
    user = relationship("User", back_populates="driver_profile")

    # RelaTIONSHIP with Routes
    routes = relationship("Route", back_populates="driver")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    # Relationships
    orders = relationship("Order", back_populates="delivery_location")
    route_stops = relationship("RouteStop", back_populates="location")



class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    delivery_location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    status = Column(String, nullable=False, default=OrderStatus.PENDING.value)
    special_instructions = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=text('now()'))


    # Relationships
    delivery_location = relationship("Location", back_populates="orders")
    route_stops = relationship("RouteStop", back_populates="order")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")



class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=True)
    dimensions = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    # Relationship
    order = relationship("Order", back_populates="items")



class RouteStatus(str, enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"   



class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String, nullable=False, default=RouteStatus.PLANNED.value)
    total_distance = Column(Integer, nullable=True)
    estimated_time = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=text('now()'))

    # Relationships
    driver = relationship("Driver", back_populates="routes")
    stops = relationship("RouteStop", back_populates="route", cascade="all, delete-orphan")



class RouteStopStatus(str, enum.Enum):
    PENDING = "pending"
    ARRIVED = "arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"



class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey('routes.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    sequence = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default=RouteStopStatus.PENDING.value)
    arrival_time = Column(TIMESTAMP(timezone=True), nullable=True)
    departure_time = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    # Relationships
    route = relationship("Route", back_populates="stops")
    order = relationship("Order", back_populates="route_stops")
    location = relationship("Location", back_populates="route_stops")                


