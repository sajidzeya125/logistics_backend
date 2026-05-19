from sqlalchemy.orm import Session
from app import schemas, models
from sqlalchemy import and_
from datetime import datetime, timezone


def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    db_order = models.Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        delivery_location_id=order.delivery_location_id,
        special_instructions=order.special_instructions,
        status=models.OrderStatus.PENDING.value
    )
    db.add(db_order)
    db.flush()  # Flush to get the order ID for the items

    for item in order.items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_name=item.product_name,
            quantity=item.quantity,
            weight=item.weight,
            dimensions=item.dimensions
        )
        db.add(db_item)
    db.commit()  
    db.refresh(db_item)
    return db_order


def get_order(db: Session, order_id: int) -> models.Order:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_all_orders(db: Session,status: str = None, skip: int = 0, limit: int = 10) -> list:
    query = db.query(models.Order)
    if status:
        query = query.filter(models.Order.status == status)
    return query.offset(skip).limit(limit).all()



def update_order(db: Session, order_id: int, order_update: schemas.OrderUpdate) -> models.Order:
    db_order = get_order(db, order_id)
    if db_order:
        if order_update.customer_name is not None:
            db_order.customer_name = order_update.customer_name
        if order_update.customer_email is not None:
            db_order.customer_email = order_update.customer_email
        if order_update.customer_phone is not None:
            db_order.customer_phone = order_update.customer_phone
        if order_update.special_instructions is not None:
            db_order.special_instructions = order_update.special_instructions
        if order_update.status is not None:
            db_order.status = order_update.status
        db_order.updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        db.commit()
        db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    db_order = get_order(db, order_id)
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False


def get_pending_orders(db: Session, skip: int = 0, limit: int = 10) -> list:
    return db.query(models.Order).filter(models.Order.status == models.OrderStatus.PENDING.value).offset(skip).limit(limit).all()