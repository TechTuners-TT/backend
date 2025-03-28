from fastapi import FastAPI
from app.api.routers import test_connection  # Ensure this is correct
from app.auth import router as auth_router  # Імпортуємо auth_router як auth_router


app = FastAPI()
app.include_router(auth_router)  # Включаємо auth_router

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API!"}

# Include the router for the test connection
app.include_router(test_connection.router)

@app.on_event("startup")
async def startup():
    print("Connecting to Supabase...")

@app.on_event("shutdown")
async def shutdown():
    print("Disconnecting from Supabase...")
