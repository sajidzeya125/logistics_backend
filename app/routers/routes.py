from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app import auth2
from typing import List

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/", response_model=schemas.RouteOut, status_code=status.HTTP_201_CREATED)
def create_route(
    route: schemas.RouteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Create a new route for a driver"""
    # Verify driver exists
    driver = db.query(crud.models.Driver).filter(
        crud.models.Driver.id == route.driver_id
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    return crud.route_crud.create_route(db, route.driver_id, route.date)


@router.get("/{route_id}", response_model=schemas.RouteOut)
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get route with all stops"""
    db_route = crud.route_crud.get_route(db, route_id)
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    return db_route


@router.get("/", response_model=list[schemas.RouteListOut])
def get_all_routes(
    driver_id: int = Query(None),
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get all routes with optional filters"""
    return crud.route_crud.get_all_routes(
        db, driver_id=driver_id, status=status, skip=skip, limit=limit
    )


@router.post("/{route_id}/optimize", response_model=schemas.RouteOut)
def optimize_route(
    route_id: int,
    optimize_data: schemas.RouteOptimize,
    depot_latitude: float = Query(0.0, description="Warehouse/depot latitude"),
    depot_longitude: float = Query(0.0, description="Warehouse/depot longitude"),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """
    Optimize route by assigning orders using nearest neighbor algorithm.
    
    Calculates optimal delivery sequence and distance.
    """
    db_route = crud.route_crud.add_orders_to_route(
        db,
        route_id,
        optimize_data.order_ids,
        depot_latitude,
        depot_longitude
    )
    
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    
    return db_route


@router.patch("/{route_id}/status")
def update_route_status(
    route_id: int,
    status: str = Query(..., description="New route status"),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Update route status"""
    valid_statuses = ["planned", "active", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of {valid_statuses}"
        )
    
    db_route = crud.route_crud.update_route_status(db, route_id, status)
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    return db_route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Delete a route"""
    success = crud.route_crud.delete_route(db, route_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )


@router.get("/active/all", response_model=list[schemas.RouteListOut])
def get_active_routes(
    driver_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get all active routes"""
    return crud.route_crud.get_active_routes(db, driver_id=driver_id)