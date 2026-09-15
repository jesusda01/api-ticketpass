FROM python:3-slim
WORKDIR /api-ticketpass
RUN pip install fastapi uvicorn sqlalchemy pydantic email-validator
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]