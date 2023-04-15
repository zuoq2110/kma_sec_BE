from .model import router as model_router
from .android import router as android_router
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

router.include_router(model_router)
router.include_router(android_router)