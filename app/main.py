from fastapi import FastAPI
from .routers import location, users, auth

app = FastAPI(title='Real-time Logistics API')
app.include_router(users.router)
app.include_router(auth.router)
# app.include_router(location.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Real-time Logistics API!"}