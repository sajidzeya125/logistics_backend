from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app import auth2
from datetime import datetime

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("/active/all", response_model=list[schemas.RouteStopOut])
def get_active_deliveries(
    driver_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get all active delivery stops"""
    if driver_id:
        # Get active routes for driver
        active_routes = crud.route_crud.get_active_routes(db, driver_id=driver_id)
        all_stops = []
        for route in active_routes:
            stops = crud.route_stop_crud.get_route_stops(db, route.id)
            all_stops.extend(stops)
        return all_stops
    else:
        # Get all active stops
        query = db.query(crud.models.RouteStop).filter(
            crud.models.RouteStop.status.in_([
                crud.models.RouteStopStatus.PENDING.value,
                crud.models.RouteStopStatus.ARRIVED.value,
                crud.models.RouteStopStatus.IN_PROGRESS.value
            ])
        )
        return query.all()


@router.patch("/{stop_id}/status")
def update_delivery_status(
    stop_id: int,
    status: str = Query(..., description="New delivery stop status"),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """
    Update delivery stop status.
    
    Valid statuses: pending, arrived, in_progress, completed, failed
    """
    valid_statuses = ["pending", "arrived", "in_progress", "completed", "failed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of {valid_statuses}"
        )
    
    db_stop = crud.route_stop_crud.update_route_stop_status(
        db,
        stop_id,
        status,
        arrival_time=datetime.utcnow() if status == "arrived" else None
    )
    
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery stop not found"
        )
    
    # If delivery completed, update order status
    if status == "completed":
        crud.order_crud.update_order_status(
            db,
            db_stop.order_id,
            "delivered"
        )
    
    return db_stop


@router.patch("/{stop_id}/complete")
def complete_delivery(
    stop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Mark a delivery as complete"""
    db_stop = crud.route_stop_crud.update_route_stop_status(
        db,
        stop_id,
        "completed",
        departure_time=datetime.utcnow()
    )
    
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery stop not found"
        )
    
    # Update order status to delivered
    crud.order_crud.update_order_status(
        db,
        db_stop.order_id,
        "delivered"
    )
    
    return db_stop


@router.get("/history", response_model=list[schemas.RouteStopOut])
def get_delivery_history(
    driver_id: int = Query(None),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get completed deliveries history"""
    query = db.query(crud.models.RouteStop).filter(
        crud.models.RouteStop.status == crud.models.RouteStopStatus.COMPLETED.value
    )
    
    if driver_id:
        # Join with routes to filter by driver
        query = query.join(crud.models.Route).filter(
            crud.models.Route.driver_id == driver_id
        )
    
    return query.offset(skip).limit(limit).all()


@router.get("/{stop_id}", response_model=schemas.RouteStopOut)
def get_delivery(
    stop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get delivery stop details"""
    db_stop = crud.route_stop_crud.get_route_stop(db, stop_id)
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery stop not found"
        )
    return db_stop