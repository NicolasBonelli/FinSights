"""
Script para ejecutar múltiples workers en paralelo
Configuración: 3 LlamaIndex workers + 3 LangExtract workers
"""

import asyncio
import logging
from llamaindex_worker import LlamaIndexWorker
from langextract_worker import LangExtractWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_all_workers():
    """Ejecutar múltiples instancias de workers en paralelo"""
    
    # Configuración de workers por cola
    WORKERS_PER_QUEUE = 3
    
    # Crear múltiples instancias de LlamaIndex workers
    llamaindex_workers = [
        LlamaIndexWorker() for _ in range(WORKERS_PER_QUEUE)
    ]
    
    # Crear múltiples instancias de LangExtract workers
    langextract_workers = [
        LangExtractWorker() for _ in range(WORKERS_PER_QUEUE)
    ]
    
    logger.info(f"🚀 Iniciando {WORKERS_PER_QUEUE} LlamaIndex workers...")
    logger.info(f"🚀 Iniciando {WORKERS_PER_QUEUE} LangExtract workers...")
    logger.info(f"📊 Total: {WORKERS_PER_QUEUE * 2} workers activos")
    
    # Ejecutar todos los workers en paralelo
    all_worker_tasks = []
    
    # Agregar tareas de LlamaIndex workers
    for i, worker in enumerate(llamaindex_workers):
        task = asyncio.create_task(
            worker.start_consuming(),
            name=f"LlamaIndex-Worker-{i+1}"
        )
        all_worker_tasks.append(task)
    
    # Agregar tareas de LangExtract workers
    for i, worker in enumerate(langextract_workers):
        task = asyncio.create_task(
            worker.start_consuming(),
            name=f"LangExtract-Worker-{i+1}"
        )
        all_worker_tasks.append(task)
    
    # Ejecutar todos los workers
    await asyncio.gather(*all_worker_tasks, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(run_all_workers())
    except KeyboardInterrupt:
        logger.info("🛑 Todos los workers detenidos")
