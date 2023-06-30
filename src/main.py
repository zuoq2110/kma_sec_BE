from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .infrastructure import router


app = FastAPI(title="K-Security", version="1.0.0")

app.add_middleware(middleware_class=CORSMiddleware, allow_origins=["*"])

app.include_router(router=router)


@router.head(path="/", status_code=status.HTTP_200_OK)
async def get_health():
    pass


@app.exception_handler(HTTPException)
async def handle_http_exception(_, exception: HTTPException):
    return JSONResponse(
        content={"message": exception.detail, "data": None},
        status_code=exception.status_code
    )
