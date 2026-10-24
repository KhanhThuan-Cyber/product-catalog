import sys
from pathlib import Path

# Thêm src vào sys.path để nạp an toàn các models
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from src.app.models.base import Base
from src.app.models.category import Category
from src.app.models.product import Product
from src.app.models.role import Role
from src.app.models.user import User

target_metadata = Base.metadata
