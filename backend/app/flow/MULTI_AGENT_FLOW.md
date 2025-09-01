# MULTI_AGENT_FLOW.md

Diseño del **flujo multiagente** para generación de reportes financieros sobre documentos internos de la empresa. Este documento define **nodos**, **crews**, **agentes**, **contratos de datos**, ruteo, paralelización, reintentos y la integración con el data pipeline (RabbitMQ, Redis, Elasticsearch, Azure Blob).

---

## 1) Visión general

**Entrada del sistema:**  
- Pregunta o directiva del usuario (ej. “generar reporte trimestral de liquidez y riesgos”).
- `company_id` y (opcional) lista de documentos o tags.

**Recursos de conocimiento:**  
- `chunks_small_{company_id}` (ES): chunks con BM25 + embeddings.  
- `chunks_parent_{company_id}` (ES): contexto extenso (parent).  
- `relations_{company_id}` (ES): entidades y relaciones (LangExtract).  
- Blob de Azure con PDFs originales (evidencias).

**Salida del sistema:**  
- **Executive Report (PDF/HTML)** + **Appendix técnico** con trazabilidad a fuentes.  
- **JSON estructurado** con KPIs, peers, riesgos y evidencias (para consumo downstream).  
- **Tablas/CSV** con series y métricas.  
- **Alertas** (thresholds de riesgo/variaciones relevantes).

---

## 2) Mapa del flujo (nodos y crews)
[User Query]
│
▼
[N1 Router & Policy Gate]
│ ├─ valida intención y dominio (finance)
│ └─ enruta a subflujos habilitados por el usuario
▼
[N2 Context Builder (parallel fan-out)]
├── [C2a Hybrid RAG Crew] ──► evidencia semántica (chunks_small + parent)
└── [C2b Relations RAG Crew] ─► evidencia relacional (relations ES)
(join)
▼
[N3 Analytical Layer (parallel)]
├── [C3a Finance KPIs Crew]
├── [C3b Market Peers Crew]
└── [C3c Risk Signals Crew]
(join)
▼
[N4 Synthesis & QA Crew]
│ ├─ integra outputs + dedupe + contradicciones
│ └─ valida con evidencias y cita fuentes
▼
[N5 Report Generation Crew]
├─ Executive Summary (PDF/HTML)
├─ Appendix técnico (trazabilidad)
└─ JSON/CSV (KPIs, peers, riesgos)
▼

---

## 3) Definición de Nodos & Crews

### N1) Router & Policy Gate
- **Objetivo:** entender intención, verificar permisos, normalizar pedido y **rutear** a subflujos.
- **Agentes dentro de la crew:**
  - `IntentClassifierAgent`: clasifica (KPIs / Peers / Riesgos / General Report).
  - `PolicyGuardAgent`: chequea límites (confidencialidad, alcance de fechas, empresas).
  - `ScopeRefinerAgent`: reformula prompt (añade contexto: períodos, moneda, unidad).
- **Inputs:** `user_query`, `company_id`, `opts` (ej. “incluir peers”, “solo liquidez”).
- **Outputs (contract):**
  ```json
  {
    "normalized_query": "string",
    "targets": ["kpi", "peers", "risk"],
    "time_scope": {"from":"YYYY-MM-DD","to":"YYYY-MM-DD"},
    "constraints": {"currency":"USD","level_of_detail":"exec"},
    "routing": {"use_hybrid_rag": true, "use_relations_rag": true}
  }
Notas: si targets está vacío, por defecto: "kpi","risk".

N2) Context Builder (fan-out)

Recupera contexto en paralelo desde dos crews y hace join.

C2a) Hybrid RAG Crew (Elasticsearch BM25 + kNN + Parent)

Agentes:

HybridRetrieverAgent: consulta chunks_small_* (BM25 + vector), fusiona (RRF).

ParentExpanderAgent: trae chunks_parent_* por parent_id y limpia redundancia.

CitationCollectorAgent: normaliza citas (doc_id, page, span).

Inputs: normalized_query, time_scope, constraints.

Outputs:

{
  "hybrid_context": [
    {"doc_id":"...", "chunk_id":"...", "parent_id":"...",
     "text":"...", "score":0.87, "page":12, "evidence_span":"..."}
  ]
}

C2b) Relations RAG Crew (LangExtract en ES)

Agentes:

RelationQueryAgent: queries sobre relations_* (por entity_class, atributos y período).

RelationGrouperAgent: agrupa por métrica/periodo/company para análisis.

TracebackAgent: arma backreferences a doc_id / evidence_text.

Outputs:

{
  "relational_context": [
    {"entity_class":"Metric","entity_text":"EBITDA",
     "attributes":{"period":"Q2-2025","value":"$3.2M"},
     "evidence":{"doc_id":"...","chunk_id":"...","span":"..."}}
  ]
}


Join (N2):

Unificador: ContextMergerNode hace deduplicación, score fusion y elimina contradicciones evidentes (marca para QA si detecta conflicto).

N3) Analytical Layer (parallel)
C3a) Finance KPIs Crew

Agentes:

KPIExtractorAgent: parsea métricas (ventas, margen bruto/operativo, EBITDA, flujo de caja, ROE/ROA, liquidez corriente, razón rápida, endeudamiento, cobertura de intereses).

TimeSeriesAgent: alinea períodos (mensual/trimestral/anual), calcula variaciones y CAGR.

ValidationAgent: cross-check con relaciones extraídas vs. texto (consistencia).

Outputs:

{
  "kpis":[
    {"name":"Revenue","period":"Q2-2025","value":10000000,"currency":"USD",
     "delta_qoq":0.12,"delta_yoy":0.18,"sources":[...]}
  ],
  "notes":["..."]
}

C3b) Market Peers Crew

Agentes:

PeerSelectorAgent: define peer set (si existe en base o config).

BenchmarkingAgent: compara KPIs normalizados (márgenes, palancas).

PositioningAgent: ranking y gaps (oportunidades/mejoras).

Outputs:

{
  "peers":[
    {"peer":"CompX","metric":"EBITDA margin","ours":0.21,"peer":0.18,"gap":0.03}
  ],
  "insights":["..."]
}

C3c) Risk Signals Crew

Agentes:

RiskPatternAgent: heurísticas y reglas (alto leverage, caída ventas, concentración clientes).

AnomalyAgent: outliers en series (z-score/IQR) + triggers (covenants hipotéticos).

ComplianceAgent: banderas (falta de estados, atrasos, auditorías adversas si existen).

Outputs:

{
  "risks":[
    {"type":"Liquidity","signal":"Quick ratio < 1","period":"Q2-2025",
     "severity":"high","evidence":[...],"recommendation":"..."}
  ]
}


Join (N3): AnalysisJoinNode agrega KPIs + Peers + Riesgos en un AnalysisBundle:

{
  "analysis_bundle":{
    "kpis":[...],
    "peers":[...],
    "risks":[...],
    "context_refs":[...]
  }
}

N4) Synthesis & QA Crew

Agentes:

SynthesisAgent: narrativa ejecutiva (qué pasó / por qué / so what).

ConflictResolverAgent: resuelve inconsistencias (marca “needs review” si persisten).

FactCheckAgent: verifica citas (muestra doc_id + página + span).

Output:

{
  "synthesis":{
    "executive_summary":"...",
    "key_takeaways":["...","..."],
    "limitations":["..."],
    "citations":[{"doc_id":"...","page":12,"span":"..."}]
  }
}

N5) Report Generation Crew

Agentes:

ReportFormatterAgent: maqueta PDF/HTML (portada, índice, secciones).

AppendixAgent: trazabilidad + tablas y series (CSV/Excel).

SchemaEmitterAgent: emite JSON final (contrato estable para backend).

Output final (contratos):

report.pdf (o report.html)

appendix.pdf|html

kpis.csv, series.csv

report.json

{
  "company_id":"...",
  "period":{"from":"...","to":"..."},
  "kpis":[...],
  "peers":[...],
  "risks":[...],
  "citations":[...],
  "generated_at":"ISO-8601"
}

4) Ruteo, paralelismo y listeners en CrewAI

Router principal (N1):

Listener de entrada: recibe user_query.

Emite RoutingPlan al Bus (in-memory o pub/sub de CrewAI).

Fan-out (N2):

Hybrid RAG y Relations RAG arrancan en paralelo (listeners suscritos a RoutingPlan).

Publican hybrid_context y relational_context en tópicos separados; ContextMergerNode escucha ambos y hace join.

Analytical Layer (N3):

Finance KPIs, Market Peers, Risk Signals consumen merged_context en paralelo.

AnalysisJoinNode escucha a los tres y hace join.

Backpressure y timeouts:

Cada crew tiene timeout_sla y max_retries.

Si falla un subflujo, el resto continúa y N4 reporta limitaciones.

Estado y caching (Redis):

Clave por session_id para almacenar merged_context y analysis_bundle (evitar recomputar en follow-ups).

TTL de contexto configurable (ej. 60 min).

5) Herramientas (tools) por agente (sugerencia)

RAG tools

ElasticHybridSearchTool: busca en chunks_small_* con BM25+vector y rescora.

ParentFetchTool: trae chunks_parent_* por parent_id.

RelationsSearchTool: consultas sobre relations_* (por entity_class, attributes.period, etc.).

BlobEvidenceTool: genera URL firmada/sas para citas (opcional, o path interno).

Análisis

KpiCalcTool: normaliza, convierte monedas, calcula variaciones.

PeerBenchTool: ranking/gaps; si no hay peers internos, cae a “solo histórico”.

RiskHeuristicsTool: reglas + thresholds configurables (YAML).

AnomalyTool: detecta outliers simples en series.

Output

PDFRendererTool / HTMLRendererTool

CSVEmitterTool

JSONSchemaTool (valida contra schema de report.json).

6) Contratos de datos (esenciales)
6.1. ContextItem
{
  "doc_id":"string",
  "chunk_id":"string",
  "parent_id":"string",
  "text":"string",
  "page": 12,
  "score": 0.0,
  "evidence_span": "string"
}

6.2. RelationItem
{
  "entity_class":"Metric|Value|TimePeriod|Company|Event|Risk|Trend|ComparisonTarget",
  "entity_text":"string",
  "attributes":{"key":"value"},
  "evidence":{"doc_id":"...", "chunk_id":"...", "span":"..."},
  "confidence": 0.0
}

6.3. KPIItem
{
  "name":"Revenue",
  "period":"Q2-2025",
  "value": 10000000,
  "currency":"USD",
  "delta_qoq":0.12,
  "delta_yoy":0.18,
  "sources":[{"doc_id":"...","page":12}]
}
