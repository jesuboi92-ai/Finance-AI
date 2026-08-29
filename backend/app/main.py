from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.database import engine, Base
from app.api import warehouse, transport, customer, management, auth
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    # Shutdown
    logger.info("Application shutting down")

app = FastAPI(
    title="Logistics SaaS API",
    description="Enterprise logistics platform with AI assistants",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(warehouse.router, prefix="/api/v1/warehouse", tags=["Warehouse"])
app.include_router(transport.router, prefix="/api/v1/transport", tags=["Transport"])
app.include_router(customer.router, prefix="/api/v1/customer", tags=["Customer"])
app.include_router(management.router, prefix="/api/v1/management", tags=["Management"])

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(client_id)

@app.get("/")
async def root():
    return {"message": "Welcome to Logistics SaaS API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
