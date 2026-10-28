from fastapi import APIRouter

# Resource routers (auth, products, sales, ...) are included here as each phase lands.
api_router = APIRouter(prefix="/api/v1")
