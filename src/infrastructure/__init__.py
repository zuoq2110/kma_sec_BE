from fastapi import APIRouter
from .model import router as model_router
from .android import router as android_router
from .windows import router as windows_router
from .user import router as user_router
from .pdf import router as pdf_router

router = APIRouter(prefix="/api/v1")

router.include_router(router=model_router)
router.include_router(router=android_router)
router.include_router(router=windows_router)
router.include_router(router=user_router)
router.include_router(router=pdf_router)
