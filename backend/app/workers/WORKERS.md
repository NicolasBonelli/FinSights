# Workers - Data Pipeline

Este documento describe la lógica de los **workers** que procesan los documentos enviados desde RabbitMQ y almacenan los resultados en **Elasticsearch**.

---

## Worker 1: LlamaIndex Worker

**Cola:** `llamaindex_queue`  
**Objetivo:** Procesamiento de chunks y embeddings para RAG con Document Parent Retriever.

### Flujo de trabajo
1. **Descarga del archivo** desde **Azure Blob Storage** (usando el `file_id` recibido desde la cola).
2. **Preprocesamiento con LlamaIndex**:
   - Aplicar **Recursive Character Splitting** para dividir el documento en:
     - `chunks_small` → fragmentos cortos (para embeddings y BM25).
     - `chunks_parent` → fragmentos más extensos, usados por el Document Parent Retriever .
3. **Generación de embeddings**:
   - Crear embeddings solo para `chunks_small`.
   - Modelo: `sentence-transformers` (o el configurado en el entorno).
4. **Guardar en Elasticsearch**:
   - Índice `chunks_small`
     - `id`
     - `doc_id`
     - `chunk_text`
     - `parent_id`
     - `embedding`
     - `bm25` (campo indexado por Elasticsearch automáticamente).
   - Índice `chunks_parent`
     - `id`
     - `doc_id`
     - `parent_text`

---

## Worker 2: LangExtract Worker

**Cola:** `langextract_queue`  
**Objetivo:** Extracción de entidades y relaciones semánticas del documento.

### Flujo de trabajo
1. **Descarga del archivo** desde **Azure Blob Storage**.
2. **Procesamiento con LangExtract**:
   - Detectar **entidades clave** (organizaciones, fechas, métricas, etc.).
   - Identificar **relaciones** entre entidades.
3. **Guardar en Elasticsearch**:
   - Índice `relations`
     - `id`
     - `doc_id`
     - `entity_1`
     - `entity_2`
     - `relation_type`
     - `evidence_text` (fragmento del documento donde aparece la relación).

---

## Consideraciones

- **Idempotencia:** antes de insertar en Elasticsearch, verificar si el documento ya fue procesado (Redis maneja la lógica inicial).
- **Batching:** si el documento es grande, procesar por lotes para optimizar memoria y requests.
- **Errores:** usar reintentos automáticos (RabbitMQ + ack/nack).
- **Escalabilidad:** cada worker puede tener múltiples instancias escuchando la misma cola.

---

## Resumen de Índices en Elasticsearch

- **`chunks_small`** → chunks pequeños con embeddings + BM25 (para búsquedas híbridas).
- **`chunks_parent`** → chunks padres con texto extendido (para Document Parent Retriever).
- **`relations`** → entidades y relaciones extraídas por LangExtract.
