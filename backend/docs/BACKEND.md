# BACKEND.md

## Visión General
El backend se construye con **FastAPI** y actúa como la capa de orquestación y exposición de servicios.  
Conecta el frontend (ej. Streamlit o dashboard interno) con los workers (Celery + RabbitMQ) y con los agentes (CrewAI).

---

## Endpoints Clave

### 1. `/upload`
- **Método**: `POST`
- **Entrada**: PDF de la empresa (multipart/form-data).
- **Acciones**:
  - Subir PDF a **Azure Blob Storage**.
  - Registrar metadata en Redis.
  - Enviar tarea de procesamiento inicial a Celery (`ingestion_agent`).

---

### 2. `/ask`
- **Método**: `POST`
- **Entrada**: JSON con:
  ```json
  {
    "company_id": "123",
    "question": "¿Cuál fue la evolución de la rentabilidad trimestral?"
  }
