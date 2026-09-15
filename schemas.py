# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Esquema para Evento
class EventoBase(BaseModel):
    titulo: str
    categoria: str
    lugar: str
    fecha: str
    precio: float
    banner_url: str

class EventoResponse(EventoBase):
    id: int

    class Config:
        from_attributes = True

# Esquema para Consulta de Persona (DNI Autocompletado)
class PersonaResponse(BaseModel):
    dni: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str

    class Config:
        from_attributes = True

# Esquemas para la Compra de Ticket
class OrdenCreate(BaseModel):
    dni_comprador: str
    id_evento: int
    correo: EmailStr
    cantidad: int

class OrdenResponse(BaseModel):
    id: int
    codigo_ticket: str
    monto_total: float
    correo: str
    fecha_compra: datetime

    class Config:
        from_attributes = True