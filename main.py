# main.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
import smtplib
from email.mime.text import MIMEText

import models, schemas, database

# Crear tablas en SQLite automáticamente al iniciar
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="TicketPass API")

# Configuración CORS para permitir peticiones desde el Frontend Apache (Puerto 8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de BD
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Poblado automático de datos iniciales
@app.on_event("startup")
def startup_populate_db():
    db = database.SessionLocal()
    # Insertar eventos si la tabla está vacía
    if not db.query(models.Evento).first():
        eventos = [
            models.Evento(
                titulo="Rock en el Parque 2026",
                categoria="Concierto",
                lugar="Parque de la Exposición",
                fecha="25 de Octubre - 20:00 hrs",
                precio=85.00,
                banner_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&q=80"
            ),
            models.Evento(
                titulo="Noche de Stand-Up Comedy",
                categoria="Teatro",
                lugar="Teatro Canout",
                fecha="12 de Noviembre - 21:00 hrs",
                precio=50.00,
                banner_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&q=80"
            ),
            models.Evento(
                titulo="Final Torneo de Pádel Lima",
                categoria="Deportes",
                lugar="Club Lawn Tennis",
                fecha="05 de Diciembre - 16:00 hrs",
                precio=35.00,
                banner_url="https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=800&q=80"
            )
        ]
        db.add_all(eventos)

    # Insertar registros ciudadanos (Mock RENIEC) si la tabla está vacía
    if not db.query(models.Persona).first():
        personas = [
            models.Persona(dni="12345678", nombres="Juan Carlos", apellido_paterno="Pérez", apellido_materno="Gómez"),
            models.Persona(dni="87654321", nombres="María Elena", apellido_paterno="Rojas", apellido_materno="Díaz"),
            models.Persona(dni="41067986", nombres="Carlos", apellido_paterno="Kiyoshi", apellido_materno="Mendoza")
        ]
        db.add_all(personas)

    db.commit()
    db.close()

# Función para envío simulado/real de correo de confirmación
def enviar_correo_confirmacion(destino: str, codigo_ticket: str, evento_titulo: str):
    mensaje_texto = f"""
    ¡Gracias por tu compra en TicketPass!

    Detalle de tu entrada:
    - Evento: {evento_titulo}
    - Código de Ticket: {codigo_ticket}
    
    Muestra este código en la puerta del evento para ingresar.
    """
    # Para demostración en entorno local / AWS Academy logueamos en consola.
    # Si configuras SMTP real, smtplib enviará el correo efectivamente.
    print(f"\n[CORREO ENVIADO A {destino}]\n{mensaje_texto}\n")

# --- ENDPOINTS ---

# 1. Obtener catálogo de eventos
@app.get("/eventos", response_model=list[schemas.EventoResponse])
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(models.Evento).all()

# 2. Consultar DNI para autocompletado de formulario
@app.get("/persona/{dni}", response_model=schemas.PersonaResponse)
def buscar_persona(dni: str, db: Session = Depends(get_db)):
    persona = db.query(models.Persona).filter(models.Persona.dni == dni).first()
    if not persona:
        raise HTTPException(status_code=404, detail="DNI no encontrado en el padrón")
    return persona

# 3. Registrar compra de ticket
@app.post("/comprar", response_model=schemas.OrdenResponse)
def procesar_compra(
    orden: schemas.OrdenCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Validar evento existente
    evento = db.query(models.Evento).filter(models.Evento.id == orden.id_evento).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Generar código único de entrada
    codigo_generado = f"TK-{uuid.uuid4().hex[:8].upper()}"
    monto_calculado = evento.precio * orden.cantidad

    nueva_orden = models.Orden(
        dni_comprador=orden.dni_comprador,
        id_evento=orden.id_evento,
        correo=orden.correo,
        cantidad=orden.cantidad,
        monto_total=monto_calculado,
        codigo_ticket=codigo_generado
    )

    db.add(nueva_orden)
    db.commit()
    db.refresh(nueva_orden)

    # Disparar envío de correo asíncrono
    background_tasks.add_task(
        enviar_correo_confirmacion,
        destino=orden.correo,
        codigo_ticket=codigo_generado,
        evento_titulo=evento.titulo
    )

    return nueva_orden