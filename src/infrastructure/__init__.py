from fastapi import APIRouter
from .model import router as model_router
from .android import router as android_router
from .windows import router as windows_router

router = APIRouter(prefix="/api/v1")

router.include_router(router=model_router)
router.include_router(router=android_router)
router.include_router(router=windows_router)
