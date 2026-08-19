from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from src.routes.user_route import router as user_routes
from src.routes.auth_route import router as auth_routes
from src.models.response_model import ResponseModel
from src.enums.error_response_enum import ErrorResponseEnum
from src.routes.support_route import router as support_route
from src.routes.sprint_route import router as sprint_route
from src.routes.project_route import router as project_route
from src.routes.group_route import router as group_route
from src.routes.file_route import router as file_route
from src.routes.task_route import router as task_route
from src.routes.document_route import router as document_route
from src.routes.testcase_route import router as testcase_route
from src.routes.session_route import router as session_route
from src.routes.work_item_route import router as work_item_route
from src.routes.profile_route import router as profile_route
from src.routes.log_route import router as log_route
from src.configs import settings
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.database import lifespan
from src.routes.chatbot_token_route import router as chatbot_token_route
from src.routes.department_route import router as department_route
from src.routes.notification_route import router as notification_route
from src.routes.meeting_route import router as meeting_route
from src.routes.shift_schedule_route import router as shift_schedule_route
from src.routes.plan_route import router as plan_route
from src.routes.evaluate_route import router as evaluate_route

app = FastAPI(
    title="Backend Daily",
    version="1.0.0",
    lifespan=lifespan,
    root_path=settings.ROOT_PATH,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect" if settings.ENABLE_DOCS else None,
)

app.include_router(support_route, prefix="/support")
app.include_router(auth_routes, prefix="/auths")
app.include_router(chatbot_token_route, prefix="/chatbot")
app.include_router(document_route, prefix="/document")
app.include_router(department_route, prefix="/department")
app.include_router(evaluate_route, prefix="/evaluate")
app.include_router(user_routes, prefix="/users")
app.include_router(file_route, prefix="/files")
app.include_router(group_route, prefix="/group")
app.include_router(log_route, prefix="/log")
app.include_router(meeting_route, prefix="/meeting")
app.include_router(notification_route, prefix="/notifications")
app.include_router(plan_route, prefix="/plan")
app.include_router(profile_route, prefix="/profile")
app.include_router(project_route, prefix="/project")
app.include_router(sprint_route, prefix="/sprint")
app.include_router(session_route, prefix="/sessions")
app.include_router(shift_schedule_route, prefix="/shift-schedule")
app.include_router(task_route, prefix="/task")
app.include_router(testcase_route, prefix="/testcase")
app.include_router(work_item_route, prefix="/work-item")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)



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
