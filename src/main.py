from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from src.routes.user_route import router as user_routes
from src.routes.auth_route import router as auth_routes
from src.models.response_model import ResponseModel
from src.enums.error_response_enum import ErrorResponseEnum
from src.routes.support_route import router as support_route
from src.configs import settings

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.database import lifespan

app = FastAPI(
    title="Backend Daily",
    version="1.0.0",
    lifespan=lifespan,
    root_path=settings.ROOT_PATH,
)

app.include_router(support_route, prefix="/support")
app.include_router(auth_routes, prefix="/auths")
app.include_router(user_routes, prefix="/users")






class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.headers.get("x-forwarded-proto") == "https":
            request.scope["scheme"] = "https"
        return await call_next(request)


app.add_middleware(ProxyHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
            "Content-Disposition",
            "Content-Length",
            "Content-Range",
            "Accept-Ranges",
            "Content-Type",
        ],
)

@app.exception_handler(HTTPException)
async def exception_handler(request: Request, exc: HTTPException):
     # http exception

    status_code = exc.status_code
    message = exc.detail

    return JSONResponse(status_code=status_code,
                        content= ResponseModel(
                            data=None,
                            success=False,
                            message= str(message),
                            ).model_dump()
                        )
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
     # http exception
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = ErrorResponseEnum.INTERNAL_ERROR.value
    return JSONResponse(status_code=status_code,
                        content= ResponseModel(
                            data=None,
                            success=False,
                            message= str(message),
                            ).model_dump()
                        )
