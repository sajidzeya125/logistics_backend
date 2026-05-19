from fastapi import FastAPI
from .routers import locations, users, auth, orders, routes, deliveries

app = FastAPI(title='Real-time Logistics API')


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(locations.router)
app.include_router(orders.router)
app.include_router(routes.router)
app.include_router(deliveries.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Real-time Logistics API!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}