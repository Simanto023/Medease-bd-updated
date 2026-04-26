from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.database import Base
import uuid


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_name = Column(String(500), nullable=False, index=True)
    generic_name = Column(Text, nullable=False)
    company = Column(String(500), nullable=False, index=True)
    strength = Column(String(200))
    form = Column(String(100))
    price_bdt = Column(Float)
    embedding = Column(Vector(384))  # 384-dim for all-MiniLM-L6-v2

    def to_dict(self):
        return {
            "id": str(self.id),
            "brand_name": self.brand_name,
            "generic_name": self.generic_name,
            "company": self.company,
            "strength": self.strength,
            "form": self.form,
            "price_bdt": self.price_bdt,
        }
