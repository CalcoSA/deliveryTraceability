from app.api.applicationUserController import router as applicationUserRouter
from app.api.deliveryRecordController import router as deliveryRecordRouter
from app.infrastructure.logging.loggerConfig import setupLogging, getLogger
from app.api.deliveryReportController import router as deliveryReportRouter
from app.api.pointSaleEmailController import router as pointSaleEmailRouter
from app.api.absenceTypeController import router as absenceTypeRouter
from app.api.domiciliaryController import router as domiciliaryRouter
from app.api.menuOptionController import router as menuOptionRouter
from app.api.pointSaleController import router as pointSaleRouter
from app.api.parameterController import router as parameterRouter
from app.infrastructure.db.connection import Base, engine
from app.api.authController import router as authRouter
from app.api.roleController import router as roleRouter
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.db.base import Base
from fastapi import FastAPI, Request
from time import time

setupLogging()
logger = getLogger(__name__)

app = FastAPI(title="Delivery Traceability API", version="1.0.0")

@app.middleware("http")
async def logRequests(request: Request, call_next):
    startTime = time()
    try:
        response = await call_next(request)
        durationMs = round((time() - startTime) * 1000, 2)
        logger.info(
            "Request finalizado | method=%s | path=%s | status=%s | duration_ms=%s | client=%s",
            request.method,
            request.url.path,
            response.status_code,
            durationMs,
            request.client.host if request.client else "unknown"
        )
        return response
    except Exception:
        durationMs = round((time() - startTime) * 1000, 2)
        logger.exception(
            "Error no controlado en request | method=%s | path=%s | duration_ms=%s | client=%s",
            request.method,
            request.url.path,
            durationMs,
            request.client.host if request.client else "unknown"
        )
        raise

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://qa-deliverytraceability.calcoweb.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(pointSaleRouter)
app.include_router(domiciliaryRouter)
app.include_router(roleRouter)
app.include_router(menuOptionRouter)
app.include_router(applicationUserRouter)
app.include_router(authRouter)
app.include_router(parameterRouter)
app.include_router(deliveryRecordRouter)
app.include_router(deliveryReportRouter)
app.include_router(absenceTypeRouter)
app.include_router(pointSaleEmailRouter)

@app.get("/")
def root():
    logger.info("Health check ejecutado")
    return { "message": "API deliveryTraceability funcionando correctamente" }