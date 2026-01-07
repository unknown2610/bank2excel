from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from processor import process_bank_statement

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory job status (replace with database for production)
jobs = {}

@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    conversion_type: str = Form("generic")
):
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    jobs[job_id] = {
        "status": "processing", 
        "progress": 0, 
        "message": "File uploaded",
        "original_filename": file.filename
    }
    
    background_tasks.add_task(process_bank_statement, file_path, job_id, jobs, OUTPUT_DIR, conversion_type)
    
    return {"job_id": job_id}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/download/{job_id}")
async def download_file(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    file_path = job["output_file"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Construct a friendly filename
    original_name = job.get("original_filename", "statement")
    # Remove extension from original and add _converted.xlsx
    clean_name = os.path.splitext(original_name)[0]
    download_name = f"{clean_name}_converted.xlsx"
    
    return FileResponse(
        file_path, 
        filename=download_name, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
