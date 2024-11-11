from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import zeep
import requests

# Define the request model
class GetDownloadFileRequest(BaseModel):
    User: str
    Password: str
    FilePath: str

# Define the WCF Service URLs
SERVICE_URL = "https://vinlink.ibc.ca/ProductService/ProductDownload.svc"

# Create a Zeep client for SOAP-based communication with the WCF service
client = zeep.Client(SERVICE_URL)

# Helper function to call the WCF service to get the download file
def call_get_download_file(request_data: GetDownloadFileRequest):
    try:
        service = client.bind("ProductDownloadClient")
        request = {
            'User': request_data.User,
            'Password': request_data.Password,
            'FilePath': request_data.FilePath
        }
        response = service.GetDownloadFile(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling GetDownloadFile: {str(e)}")

# Create an APIRouter instance
router = APIRouter()

@router.post("/get-download-file")
async def get_download_file(request_data: GetDownloadFileRequest):
    """
    Get the product file by providing the file path.
    """
    response = call_get_download_file(request_data)
    if response:
        file_path = request_data.FilePath.split("/")[-1]
        with open(f"downloaded_{file_path}", "wb") as file:
            file.write(response)
        return {"message": f"File saved as 'downloaded_{file_path}'"}
    else:
        raise HTTPException(status_code=404, detail="File not found.")
