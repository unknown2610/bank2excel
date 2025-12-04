import pdfplumber
import pandas as pd
import pytesseract
from PIL import Image
import os
import time
from rpt_parser import parse_rpt_file

# Set tesseract path if needed (e.g. Windows default)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_bank_statement(file_path, job_id, jobs, output_dir):
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Starting processing..."

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        all_tables = []

        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                for i, page in enumerate(pdf.pages):
                    # Update progress every 10 pages or 10%
                    if i % 10 == 0 or i == total_pages - 1:
                        progress = 10 + int((i / total_pages) * 80)
                        jobs[job_id]["progress"] = progress
                        jobs[job_id]["message"] = f"Processing page {i+1} of {total_pages}"
                    
                    tables = page.extract_tables()
                    for table in tables:
                        # Basic cleaning: remove empty rows/cols if needed
                        # For now, just append
                        df = pd.DataFrame(table)
                        all_tables.append(df)
                        
        elif ext in [".jpg", ".jpeg", ".png"]:
            jobs[job_id]["message"] = "Processing image (OCR)..."
            # Basic OCR implementation
            # This is a placeholder for more complex table extraction from images
            text = pytesseract.image_to_string(Image.open(file_path))
            # Naive approach: split by lines and tabs/spaces
            lines = text.split('\n')
            data = [line.split() for line in lines if line.strip()]
            all_tables.append(pd.DataFrame(data))
            jobs[job_id]["progress"] = 90
            
        elif ext == ".rpt":
            jobs[job_id]["message"] = "Parsing RPT file..."
            df = parse_rpt_file(file_path)
            if not df.empty:
                all_tables.append(df)
            jobs[job_id]["progress"] = 90

        else:
            raise ValueError("Unsupported file format")

        jobs[job_id]["message"] = "Generating Excel file..."
        
        if not all_tables:
             raise ValueError("No tables found in the document")

        # Combine all tables
        # This is tricky as tables might have different columns. 
        # For a bank statement, we assume a consistent structure or we just dump them sequentially.
        # A better approach for 2000 pages is to try to align them.
        # For this MVP, we will concatenate them.
        
        final_df = pd.concat(all_tables, ignore_index=True)
        
        output_filename = f"{job_id}.xlsx"
        output_path = os.path.join(output_dir, output_filename)
        
        final_df.to_excel(output_path, index=False, header=False)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Conversion complete"
        jobs[job_id]["output_file"] = output_path

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = str(e)
        print(f"Error processing job {job_id}: {e}")
