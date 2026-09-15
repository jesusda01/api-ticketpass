# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    categoria = Column(String)
    lugar = Column(String)
    fecha = Column(String)
    precio = Column(Float)
    banner_url = Column(String)

    ordenes = relationship("Orden", back_populates="evento")


class Persona(Base):
    __tablename__ = "personas"

    dni = Column(String(8), primary_key=True, index=True)
    nombres = Column(String)
    apellido_paterno = Column(String)
    apellido_materno = Column(String)


class Orden(Base):
    __tablename__ = "ordenes"

    id = Column(Integer, primary_key=True, index=True)
    dni_comprador = Column(String(8), ForeignKey("personas.dni"))
    id_evento = Column(Integer, ForeignKey("eventos.id"))
    correo = Column(String)
    cantidad = Column(Integer)
    monto_total = Column(Float)
    codigo_ticket = Column(String, unique=True, index=True)
    fecha_compra = Column(DateTime, default=datetime.utcnow)

    evento = relationship("Evento", back_populates="ordenes")