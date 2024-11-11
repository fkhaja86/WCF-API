from fastapi import FastAPI, HTTPException
from app.routers import prepare_download, get_download
from pydantic import BaseModel
import zeep
from datetime import datetime

app = FastAPI()


# Include the routers
app.include_router(prepare_download.router)
app.include_router(get_download.router)

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

class GetDownloadFileRequest(BaseModel):
    User: str
    Password: str
    FilePath: str

# Define the WCF Service URLs
SERVICE_URL = "https://vinlink.ibc.ca/ProductService/ProductDownload.svc"

# Create a Zeep client for SOAP-based communication with the WCF service
client = zeep.Client(SERVICE_URL)

# Helper function to call the WCF service to prepare the download file
@app.post("/prepare-download")
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

@app.post("/prepare_download_file", response_model=PrepareDownloadFileResponse)
async def prepare_download_file(request_data: PrepareDownloadFileRequest):
    """
    Prepare the product file for download.
    """
    response = call_prepare_download_file(request_data)
    # Process and return the response accordingly
    return {
        "ErrorMessage": response.ErrorMessage,
        "FilePath": response.FilePath
    }

# @app.post("/get_download_file")
# async def get_download_file(request_data: GetDownloadFileRequest):
#     """
#     Get the product file by providing the file path.
#     """
#     response = call_get_download_file(request_data)
#     # The file is returned as a byte array, so you could save it to disk or process it.
#     if response:
#         file_path = request_data.FilePath.split("/")[-1]
#         with open(f"downloaded_{file_path}", "wb") as file:
#             file.write(response)
#         return {"message": f"File saved as 'downloaded_{file_path}'"}
#     else:
#         raise HTTPException(status_code=404, detail="File not found.")

# To run the FastAPI app, use:
# uvicorn script_name:app --reload
