from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.database import Base
import uuid


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_name = Column(String(500), nullable=False, index=True)
    type = Column(String(50))
    generic_name = Column(Text, nullable=False)
    company = Column(String(500), nullable=False, index=True)
    strength = Column(String(200))
    form = Column(String(100))
    package_info = Column(String(500))
    price_bdt = Column(Float)
    embedding = Column(Vector(384))

    def to_dict(self):
        return {
            "id": str(self.id),
            "brand_name": self.brand_name,
            "generic_name": self.generic_name,
            "company": self.company,
            "strength": self.strength,
            "form": self.form,
            "package_info": self.package_info,
            "price_bdt": self.price_bdt,
        }


class Generic(Base):
    __tablename__ = "generics"

    id = Column(Integer, primary_key=True)
    generic_name = Column(Text, nullable=False, index=True)
    drug_class = Column(String(500))
    indication = Column(String(1000))
    indication_desc = Column(Text)
    pharmacology = Column(Text)
    dosage = Column(Text)
    side_effects = Column(Text)
    precautions = Column(Text)
    embedding = Column(Vector(384))

    def to_dict(self):
        return {
            "id": self.id,
            "generic_name": self.generic_name,
            "drug_class": self.drug_class,
            "indication": self.indication,
            "indication_desc": self.indication_desc,
            "pharmacology": self.pharmacology,
            "dosage": self.dosage,
            "side_effects": self.side_effects,
            "precautions": self.precautions,
        }