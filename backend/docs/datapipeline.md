# Data Pipeline - Arquitectura Inicial

Este documento describe el flujo inicial del **Data Pipeline** para el sistema de reportes automatizados.

---

## Flujo General

1. **Ingreso del archivo**
   - El usuario sube un PDF desde la interfaz (**Streamlit** o similar).
   - El **backend (FastAPI)** recibe la solicitud y almacena el archivo en **Azure Blob Storage**.

2. **Chequeo de cache**
   - El nombre del archivo se consulta en **Redis** para verificar si ya fue procesado recientemente.
   - Estrategia:
     - Si el archivo **ya existe en Redis** → se descarta el procesamiento.
     - Si el archivo **no existe en Redis**:
       - Se agrega el nombre del archivo con un TTL configurable (ej: 24h).
       - Se continúa con el procesamiento.

3. **Envío a colas de RabbitMQ**
   - El backend envía el nombre del archivo a **dos colas distintas** en **RabbitMQ**:
     - **Cola `llamaindex_queue`** → procesamiento de chunks, embeddings y Document Parent Retriever.
     - **Cola `langextract_queue`** → extracción de relaciones y entidades con LangExtract.

4. **Workers**
   - Existen workers especializados que escuchan cada cola:
     - **Worker LlamaIndex**:
       - Descarga el archivo desde **Azure Blob Storage**.
       - Aplica **chunking** (chunks pequeños + chunks padres).
       - Genera **embeddings** de los chunks pequeños.
       - Guarda la información en **Elasticsearch**:
         - `chunks_small` (texto corto + embeddings + BM25).
         - `chunks_parent` (texto extendido, sin embeddings).
     - **Worker LangExtract**:
       - Descarga el archivo desde **Azure Blob Storage**.
       - Extrae relaciones, entidades y conexiones semánticas.
       - Guarda la información en el índice `relations` en **Elasticsearch**.

---

## Componentes Principales

- **Frontend:** Streamlit (interfaz de carga).
- **Backend:** FastAPI.
- **Almacenamiento:** Azure Blob Storage.
- **Cache:** Redis (control de duplicados).
- **Mensajería:** RabbitMQ (colas separadas para LlamaIndex y LangExtract).
- **Workers:** Procesadores especializados.
- **Base de Datos:** Elasticsearch (índices `chunks_small`, `chunks_parent`, `relations`).

---

## Ventajas de esta Arquitectura

- **Escalabilidad:** Workers desacoplados procesan en paralelo según la carga.
- **Robustez:** Redis evita reprocesamiento innecesario.
- **Flexibilidad:** Cada cola puede escalar de manera independiente.
- **Optimización para RAG:** Soporte para `Document Parent Retriever` + búsqueda híbrida (BM25 + embeddings).

---