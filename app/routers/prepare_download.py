from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import zeep

# Define the request and response models based on the documentation
class PrepareDownloadFileRequest(BaseModel):
    User: str
    Password: str
    Product: str
    PublicationYear: str
    Language: str
    StartDate: datetime
    EndDate: datetime

class PrepareDownloadFileResponse(BaseModel):
    ErrorMessage: list
    FilePath: str

# Define the WCF Service URLs
SERVICE_URL = "https://vinlink.ibc.ca/ProductService/ProductDownload.svc"

# Create a Zeep client for SOAP-based communication with the WCF service
client = zeep.Client(SERVICE_URL)

# Helper function to call the WCF service to prepare the download file
def call_prepare_download_file(request_data: PrepareDownloadFileRequest):
    try:
        service = client.bind("ProductDownloadClient")
        request = {
            'User': request_data.User,
            'Password': request_data.Password,
            'Product': request_data.Product,
            'PublicationYear': request_data.PublicationYear,
            'Language': request_data.Language,
            'StartDate': request_data.StartDate.isoformat(),
            'EndDate': request_data.EndDate.isoformat()
        }
        response = service.PrepareDownloadFile(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling PrepareDownloadFile: {str(e)}")

# Create an APIRouter instance
router = APIRouter()

@router.post("/prepare-download", response_model=PrepareDownloadFileResponse)
async def prepare_download_file(request_data: PrepareDownloadFileRequest):
    """
    Prepare the product file for download.
    """
    response = call_prepare_download_file(request_data)
    return {
        "ErrorMessage": response.ErrorMessage,
        "FilePath": response.FilePath
    }
