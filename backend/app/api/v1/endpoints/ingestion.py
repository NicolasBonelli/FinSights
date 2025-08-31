"""
API endpoint for file ingestion.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.core.azure_storage import azure_blob_service
from app.models.responses import IngestionResponse

router = APIRouter()

@router.post(
    "/upload",
    response_model=IngestionResponse,
    summary="Upload a file for analysis",
    description="Uploads a PDF file to Azure Blob Storage for further processing.",
)
async def upload_file(
    company_id: str,
    file: UploadFile = File(..., description="The PDF file to be analyzed."),
):
    """
    Handles the file upload process:
    1. Validates the file type.
    2. Uploads the file to Azure Blob Storage.
    3. Returns the URL of the stored file.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Please upload a PDF.",
        )

    try:
        file_content = await file.read()
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
        
        return IngestionResponse(
            message="File uploaded successfully",
            file_url=blob_url,
            filename=file.filename,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )
