# AGENTS.md

## Visión General
Este proyecto implementa un **sistema multiagente con CrewAI** orientado a la generación de reportes financieros automatizados.  
El flujo procesa **PDFs con información económica de la empresa**, los enriquece con embeddings y relaciones semánticas, y produce salidas estructuradas y útiles para usuarios humanos y sistemas automatizados.

Los agentes se dividen en:
- **Agentes de Recuperación (RAG)**
- **Agentes Analíticos**
- **Agentes de Integración y Orquestación**

---

## Agentes

### 1. 📂 Ingestion Agent
- **Objetivo**: recibir PDFs financieros desde Azure Blob Storage.
- **Tareas**:
  - Extraer texto de los PDFs.
  - Hacer *chunking semántico* con LlamaIndex (Document + Parent Retriever).
  - Enviar chunks a las colas de RabbitMQ.
  - Guardar metadatos de documentos en Redis (para evitar reprocesamientos).

---

### 2. 🔎 RAG Agents
Se usan dos agentes especializados en recuperación de información:

- **Hybrid RAG Agent**
  - Busca información en **Elasticsearch** con **Hybrid Search** (vectorial + BM25).
  - Devuelve contexto enriquecido y balanceado entre relevancia semántica y keyword search.

- **LangExtract RAG Agent**
  - Explora las **relaciones extraídas por LangExtract**.
  - Permite consultas más estructurales (e.g., relaciones entre KPIs, vínculos con áreas de negocio, dependencias financieras).

---

### 3. 📊 Analytical Crews

- **Finance KPIs Crew**
  - Calcula y contextualiza métricas financieras clave (liquidez, rentabilidad, deuda, márgenes, flujos de caja).
  - Valida la consistencia de los KPIs extraídos.

- **Market Peers Crew**
  - Compara la empresa contra benchmarks o competidores.
  - Genera análisis de posicionamiento relativo.

- **Risk Signals Crew**
  - Identifica señales de alerta (endeudamiento excesivo, caídas de ingresos, dependencia de pocos clientes).
  - Detecta riesgos regulatorios o de cumplimiento.

---

### 4. 🧩 Integration & Reporting Agent
- Integra los outputs de todas las crews.
- Produce:
  - **Executive Report (PDF)** con conclusiones clave.
  - **Dashboards/Tablas dinámicas** (Excel, CSV o HTML interactivo).
  - **Archivo JSON estructurado** con KPIs y evidencias.
  - **Alertas e Insights accionables** (riesgos detectados, oportunidades de optimización).

---

## Routing y Flujos en CrewAI
- El flujo principal recibe una **directiva o pregunta del usuario**.
- Listener inicial → determina qué agentes activar.
- RAG Agents trabajan en paralelo (Hybrid + LangExtract).
- Analytical Crews trabajan en paralelo con resultados del RAG.
- Integration Agent espera a que todos terminen (join node) y produce la salida final.

---
