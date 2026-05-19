from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app import auth2

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Create a new order"""
    # Verify location exists
    location = crud.location_crud.get_location(db, order.delivery_location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery location not found"
        )
    
    return crud.order_crud.create_order(db, order)


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get order by ID"""
    db_order = crud.order_crud.get_order(db, order_id)
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return db_order


@router.get("/", response_model=list[schemas.OrderListOut])
def get_all_orders(
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get all orders with optional status filter"""
    return crud.order_crud.get_all_orders(db, status=status, skip=skip, limit=limit)


@router.put("/{order_id}", response_model=schemas.OrderOut)
def update_order(
    order_id: int,
    order_update: schemas.OrderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Update an order"""
    db_order = crud.order_crud.update_order(db, order_id, order_update)
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return db_order


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str = Query(..., description="New order status"),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Update order status"""
    valid_statuses = ["pending", "assigned", "in_transit", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of {valid_statuses}"
        )
    
    db_order = crud.order_crud.update_order_status(db, order_id, status)
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return db_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Delete an order"""
    success = crud.order_crud.delete_order(db, order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )


@router.get("/pending/all", response_model=list[schemas.OrderListOut])
def get_pending_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth2.get_current_user)
):
    """Get all pending orders not assigned to any route"""
    return crud.order_crud.get_pending_orders(db, skip=skip, limit=limit)