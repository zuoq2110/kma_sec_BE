from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .infrastructure import router


app = FastAPI(title="K-Security", version="1.0.0")

app.add_middleware(middleware_class=CORSMiddleware, allow_origins=["*"])

app.include_router(router=router)


@app.exception_handler(HTTPException)
async def handle_http_exception(_, exception: HTTPException):
    return JSONResponse(
        content={"message": exception.detail, "data": None},
        status_code=exception.status_code
    )
