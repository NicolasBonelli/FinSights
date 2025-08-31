"""
API endpoint for file ingestion.
"""

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.app.core.config import get_settings
from backend.app.core.azure_storage import azure_blob_service
from backend.app.core.rabbitmq import rabbitmq_client
from backend.app.models.responses import IngestionResponse
import hashlib
from backend.app.core.redis_client import get_redis_client



router = APIRouter()
settings = get_settings()



@router.post(
    "/upload",
    response_model=IngestionResponse,
    summary="Upload a file for analysis",
    description="Uploads a PDF file to Azure Blob Storage and triggers the processing pipeline.",
)
async def upload_file(
    company_id: str,
    file: UploadFile = File(..., description="The PDF file to be analyzed."),
):
    """
    Handles the file upload process:
    1. Validates the file type.
    2. Uploads the file to Azure Blob Storage.
    3. Publishes a message to RabbitMQ to start the processing pipeline.
    4. Returns the URL of the stored file and a document ID.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Please upload a PDF.",
        )

    try:
        file_content = await file.read()
        # 1. Check if file has already been processed
        redis = await get_redis_client()
        file_hash = hashlib.sha256(file_content).hexdigest()
        redis_key = f"processed:{company_id}:{file_hash}"
        if await redis.exists(redis_key):
            raise HTTPException(
                status_code=409,
                detail="This file has already been processed recently."
            )
        # 2. Upload redis key TTL (estimated 24h)
        await redis.set(redis_key, "1", ex=60*60*24)
        # 3. Extract file_id (blob_name) from URL
        blob_url = await azure_blob_service.upload_file(
            file_content=file_content,
            filename=file.filename,
            company_id=company_id,
            content_type=file.content_type,
        )
        
        if not blob_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to Azure Blob Storage.",
            )

        # 2. Extract file_id (blob_name) from URL
        
        file_id = blob_url.split(f"{settings.azure_container_name}/")[-1]
        doc_id = str(uuid.uuid4())
            
        # 3. Publish message to RabbitMQ
        message_body = {
            "file_id": file_id, # This is the blob_name
            "doc_id": doc_id,
            "company_id": company_id,
        }
        
        await rabbitmq_client.publish_message(
            queue_name="llamaindex_queue",
            message_body=message_body,
        )
        
        await rabbitmq_client.publish_message(
            queue_name="langextract_queue",
            message_body=message_body,
        )

        return IngestionResponse(
            message="File uploaded and processing started",
            file_url=blob_url,
            filename=file.filename,
            doc_id=doc_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )
