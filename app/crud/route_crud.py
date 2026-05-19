from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas
from app.services.route_optimizer import nearest_neighbour_optimization, calculate_route_stats
from datetime import datetime, timezone
from typing import List


def create_route(db: Session, driver_id: int, date: datetime) -> models.Route:
    db_route = models.Route(driver_id=driver_id, date=date, status=models.RouteStatus.PLANNED.value)
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route


def get_route(db: Session, route_id: int) -> models.Route:
    return db.query(models.Route).filter(models.Route.id == route_id).first()



def get_all_routes(db: Session, driver_id: int = None, date: datetime = None, status: str = None, skip: int = 0, limit: int = 10) -> list:
    query = db.query(models.Route)
    if driver_id:
        query = query.filter(models.Route.driver_id == driver_id)

    if status:
        query = query.filter(models.Route.status == status)
    return query.offset(skip).limit(limit).all()



def add_orders_to_route(db: Session, route_id: int, order_ids: List[int], depot_latitude: float, depot_longitude: float) -> models.Route:
    db_route = get_route(db, route_id)
    if not db_route:
        return None
    
    orders = db.session.query(models.Order).filter(models.Order.id.in_(order_ids)).all()

    unvisited_locations = []
    for order in orders:
        location = order.delivery_location
        unvisited_locations.append({"latitude": location.latitude,
                                    "longitude": location.longitude,
                                    "order_id": order.id,
                                    "id": location.id,
                                    "address": location.address})
        
    depot_location = (depot_latitude, depot_longitude)
    optimized_locations = nearest_neighbour_optimization(depot_location, unvisited_locations)


    all_locations = [(depot_latitude , depot_longitude)]
    for loc in optimized_locations:
        all_locations.append((loc['latitude'], loc['longitude']))

    stats = calculate_route_stats(all_locations)


    for opt_location in optimized_locations:
        db_stop = models.RouteStop(
            route_id=route_id,
            order_id=opt_location['order_id'],
            location_id=opt_location['id'],
            sequence=opt_location['sequence'],
            status=models.RouteStopStatus.PENDING.value
        )
        db.add(db_stop)

        order = db.query(models.Order).filter(models.Order.id == opt_location['order_id']).first()
        if order:
            order.status = models.OrderStatus.IN_PROGRESS.value


    db.route.total_distance = stats['total_distance']
    db.route.estimated_time = stats['estimated_time']

    db.commit()
    db.refresh(db_route)
    return db_route



def update_route_status(db: Session, route_id: int, new_status: str) -> models.Route:
    db_route = get_route(db, route_id)
    if db_route:
        db_route.status = new_status
        db_route.updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        db.commit()
        db.refresh(db_route)
    return db_route


def delete_route(db: Session, route_id: int) -> bool:
    db_route = get_route(db, route_id)
    if db_route:
        db.delete(db_route)
        db.commit()
        return True
    return False


def get_active_routes(db: Session, driver_id: int = None) -> list:
    query = db.query(models.Route).filter(models.Route.status == models.RouteStatus.ACTIVE.value)
    if driver_id:
        query = query.filter(models.Route.driver_id == driver_id)
    return query.all()