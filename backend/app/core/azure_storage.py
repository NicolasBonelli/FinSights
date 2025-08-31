"""
Azure Blob Storage utilities
"""
import logging
from typing import Optional, BinaryIO
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import AzureError
import uuid
from datetime import datetime
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


class AzureBlobService:
    """Azure Blob Storage service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[BlobServiceClient] = None
    
    async def get_client(self) -> BlobServiceClient:
        """Get Azure Blob Storage client"""
        if self.client is None:
            self.client = BlobServiceClient(
                account_url=f"https://{self.settings.azure_storage_account}.blob.core.windows.net",
                credential=self.settings.azure_storage_key
            )
        return self.client
    
    async def upload_file(
        self, 
        file_content: BinaryIO, 
        filename: str, 
        company_id: str,
        content_type: str = "application/pdf"
    ) -> Optional[str]:
        """Upload file to Azure Blob Storage"""
        try:
            client = await self.get_client()
            
            # Generate unique blob name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            blob_name = f"{company_id}/{timestamp}_{unique_id}_{filename}"
            
            # Upload file
            blob_client = client.get_blob_client(
                container=self.settings.azure_container_name,
                blob=blob_name
            )
            
            await blob_client.upload_blob(
                file_content,
                content_type=content_type,
                overwrite=True
            )
            
            # Return blob URL
            blob_url = f"https://{self.settings.azure_storage_account}.blob.core.windows.net/{self.settings.azure_container_name}/{blob_name}"
            logger.info(f"File uploaded successfully: {blob_url}")
            return blob_url
            
        except AzureError as e:
            logger.error(f"Azure error uploading file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None
    
    async def download_file(self, blob_url: str) -> Optional[bytes]:
        """Download file from Azure Blob Storage"""
        try:
            client = await self.get_client()
            
            # Extract blob name from URL
            blob_name = blob_url.split(f"{self.settings.azure_container_name}/")[-1]
            
            blob_client = client.get_blob_client(
                container=self.settings.azure_container_name,
                blob=blob_name
            )
            
            download_stream = await blob_client.download_blob()
            content = await download_stream.readall()
            
            return content
            
        except AzureError as e:
            logger.error(f"Azure error downloading file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    async def delete_file(self, blob_url: str) -> bool:
        """Delete file from Azure Blob Storage"""
        try:
            client = await self.get_client()
            
            # Extract blob name from URL
            blob_name = blob_url.split(f"{self.settings.azure_container_name}/")[-1]
            
            blob_client = client.get_blob_client(
                container=self.settings.azure_container_name,
                blob=blob_name
            )
            
            await blob_client.delete_blob()
            logger.info(f"File deleted successfully: {blob_url}")
            return True
            
        except AzureError as e:
            logger.error(f"Azure error deleting file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def build_blob_url(self, blob_name: str) -> str:
        """Build blob URL from blob name"""
        return f"https://{self.settings.azure_storage_account}.blob.core.windows.net/{self.settings.azure_container_name}/{blob_name}"
    
    async def get_file_metadata(self, blob_url: str) -> Optional[dict]:
        """Get file metadata from Azure Blob Storage"""
        try:
            client = await self.get_client()
            
            # Extract blob name from URL
            blob_name = blob_url.split(f"{self.settings.azure_container_name}/")[-1]
            
            blob_client = client.get_blob_client(
                container=self.settings.azure_container_name,
                blob=blob_name
            )
            
            properties = await blob_client.get_blob_properties()
            
            return {
                "name": blob_name,
                "size": properties.size,
                "content_type": properties.content_settings.content_type,
                "last_modified": properties.last_modified.isoformat() if properties.last_modified else None,
                "etag": properties.etag,
                "metadata": properties.metadata or {}
            }
            
        except AzureError as e:
            logger.error(f"Azure error getting file metadata: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting file metadata: {e}")
            return None


# Global service instance
azure_blob_service = AzureBlobService()
