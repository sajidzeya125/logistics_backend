from sqlalchemy.orm import Session
from app import models, schemas
from app.services.distance_calculator import haversine_distance
from sqlalchemy import and_


def create_location(db: Session, location: schemas.LocationCreate)-> models.Location:
    db_location = models.Location(latitude=location.latitude,
                                  longitude=location.longitude,
                                  address=location.address,
                                  city=location.city,
                                  postal_code=location.postal_code)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_location(db: Session, location_id: int) -> models.Location:
    return db.query(models.Location).filter(models.Location.id == location_id).first()



def get_all_locations(db: Session, skip: int = 0, limit: int = 10) -> list:
    return db.query(models.Location).offset(skip).limit(limit).all()



def find_nearby_locations(db: Session, latitude: float, longitude: float, radius_km: float = 5.0) -> list:
    locations = db.query(models.Location).all()
    nearby = []
    for location in locations:
        distance = haversine_distance(latitude, longitude, location.latitude, location.longitude)
        if distance <= radius_km:
            nearby.append({'location': location, 'distance_km': round(distance, 2)})
    nearby.sort(key=lambda x: x['distance_km'])
    return nearby



def update_location(db: Session, location_id: int, location_update: schemas.LocationCreate) -> models.Location:
    db_location = get_location(db, location_id)
    if db_location:
        db_location.latitude = location_update.latitude
        db_location.longitude = location_update.longitude
        db_location.address = location_update.address
        db_location.city = location_update.city
        db_location.postal_code = location_update.postal_code
        db.commit()
        db.refresh(db_location)
    return db_location



def delete_location(db: Session, location_id: int) -> bool:
    db_location = get_location(db, location_id)
    if db_location:
        db.delete(db_location)
        db.commit()
        return True
    return False