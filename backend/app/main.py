from app.api.applicationUserController import router as applicationUserRouter
from app.api.domiciliaryController import router as domiciliaryRouter
from app.api.menuOptionController import router as menuOptionRouter
from app.api.pointSaleController import router as pointSaleRouter
from app.api.parameterController import router as parameterRouter
from app.infrastructure.db.connection import Base, engine
from app.api.authController import router as authRouter
from app.api.roleController import router as roleRouter
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.db.base import Base
from fastapi import FastAPI

app = FastAPI(title="Delivery Traceability API", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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

@app.get("/")
def root():
    return {"message": "API deliveryTraceability funcionando correctamente"}