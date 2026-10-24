from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import SessionLocal, engine
from app.core.init_db import init_database
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router
from app.routers.users import router as users_router

# Import đầy đủ các models để SQLAlchemy Base metadata ghi nhận trước khi init
from app.models.base import Base
from app.models.category import Category
from app.models.product import Product
from app.models.role import Role
from app.models.user import User

app = FastAPI(
    title="Product Management API",
    version="1.0.0",
)

# Cấu hình CORS cho phép Frontend React (Vite) kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Tự động nâng cấp schema, tạo bảng và nạp vai trò/admin mặc định khi kết nối DB."""
    init_database(engine, SessionLocal)


# Đăng ký các router với prefix hệ thống
app.include_router(auth_router, prefix="/Thuancyber")
app.include_router(users_router, prefix="/Thuancyber")
app.include_router(products_router, prefix="/Thuancyber")
app.include_router(categories_router, prefix="/Thuancyber")


@app.get("/")
def root():
    return {"message": "Product api running"}
