from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app import auth2

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.post("/", response_model=schemas.LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db), current_user = Depends(auth2.get_current_user)):
    return crud.location_crud.create_location(db, location)


@router.get("/{location_id}", response_model=schemas.LocationOut)
def get_location(location_id: int, db: Session = Depends(get_db), current_user = Depends(auth2.get_current_user)):
    db_location = crud.location_crud.get_location(db, location_id)
    if not db_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return db_location


@router.get("/",response_model=list[schemas.LocationOut])
def get_all_locations(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db), current_user = Depends(auth2.get_current_user)):
    return crud.location_crud.get_all_locations(db, skip=skip, limit=limit)


@router.get("/nearby/search", response_model=list[dict])
def find_nearby_locations(latitude: float = Query(..., ge=-90, le=90),
                          longitude: float = Query(..., ge=-180, le=180),
                          radius_km: float = Query(5.0, gt=0),
                          db: Session = Depends(get_db),
                          current_user = Depends(auth2.get_current_user)):
    nearby = crud.location_crud.find_nearby_locations(db, latitude, longitude, radius_km)
    return [
        {
            "id": item['location'].id,
            "address": item['location'].address,
            "city": item['location'].city,
            "distance_km": item['distance_km']
        }
        for item in nearby
    ]


@router.put("/{location_id}", response_model=schemas.LocationOut)
def update_location(location_id: int, location: schemas.LocationCreate, db: Session = Depends(get_db), current_user = Depends(auth2.get_current_user)):
    db_location = crud.location_crud.update_location(db, location_id, location)
    if not db_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return db_location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db), current_user = Depends(auth2.get_current_user)):
    success = crud.location_crud.delete_location(db, location_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return None