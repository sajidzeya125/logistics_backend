from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas

def create_route_stop(db: Session, route_id: int, order_id: int, location_id: int, sequence: int) -> models.RouteStop:
    db_stop = models.RouteStop(route_id=route_id,
                               order_id=order_id,
                               location_id=location_id,
                               sequence=sequence, status=models.RouteStopStatus.PENDING.value)
    db.add(db_stop)
    db.commit()
    db.refresh(db_stop)
    return db_stop


def get_route_stop(db: Session, stop_id: int) -> models.RouteStop:
    return db.query(models.RouteStop).filter(models.RouteStop.id == stop_id).first()



def get_route_stops(db: Session, route_id: int) -> list:
    return db.query(models.RouteStop).filter(models.RouteStop.route_id == route_id).order_by(models.RouteStop.sequence).all()



def update_route_stop_status(db: Session, stop_id: int, new_status: str, arrival_time: datetime = None, departure_time: datetime = None) -> models.RouteStop:
    db_stop = get_route_stop(db, stop_id)
    if db_stop:
        db_stop.status = new_status
        if arrival_time is not None:
            db_stop.arrival_time = arrival_time
        if departure_time is not None:
            db_stop.departure_time = departure_time
        db.commit()
        db.refresh(db_stop)
    return db_stop


def delete_route_stop(db: Session, stop_id: int) -> bool:
    db_stop = get_route_stop(db, stop_id)
    if db_stop:
        db.delete(db_stop)
        db.commit()
        return True
    return False