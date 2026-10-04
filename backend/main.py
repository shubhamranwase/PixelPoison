from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import models
from database import engine
from api.routes import router

# Initialize DB
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PixelPoison API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main application routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
