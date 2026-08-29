"""Storage service for Azure Blob Storage"""
from azure.storage.blob import BlobServiceClient
from app.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        if settings.AZURE_CONNECTION_STRING:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_CONNECTION_STRING
            )
        else:
            self.blob_service_client = None
    
    def upload_file(self, file_name: str, file_content: bytes, container_name: str = None) -> str:
        """Upload file to Azure Blob Storage"""
        if not self.blob_service_client:
            logger.warning("Azure connection string not configured")
            return None
        
        try:
            container = container_name or settings.AZURE_STORAGE_CONTAINER
            blob_client = self.blob_service_client.get_blob_client(
                container=container,
                blob=file_name
            )
            blob_client.upload_blob(file_content, overwrite=True)
            logger.info(f"File uploaded: {file_name}")
            return f"azure://{container}/{file_name}"
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None
    
    def download_file(self, file_name: str, container_name: str = None) -> bytes:
        """Download file from Azure Blob Storage"""
        if not self.blob_service_client:
            logger.warning("Azure connection string not configured")
            return None
        
        try:
            container = container_name or settings.AZURE_STORAGE_CONTAINER
            blob_client = self.blob_service_client.get_blob_client(
                container=container,
                blob=file_name
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    def delete_file(self, file_name: str, container_name: str = None) -> bool:
        """Delete file from Azure Blob Storage"""
        if not self.blob_service_client:
            logger.warning("Azure connection string not configured")
            return False
        
        try:
            container = container_name or settings.AZURE_STORAGE_CONTAINER
            blob_client = self.blob_service_client.get_blob_client(
                container=container,
                blob=file_name
            )
            blob_client.delete_blob()
            logger.info(f"File deleted: {file_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

storage_service = StorageService()
