import pdfplumber
import pandas as pd
import pytesseract
from PIL import Image
import os
import re
import time
from rpt_parser import parse_rpt_file

# Set tesseract path if needed (e.g. Windows default)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_bank_statement(file_path, job_id, jobs, output_dir, conversion_type="generic"):
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Starting processing..."

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Explicit Conversion Types
        if conversion_type == "jk_bank":
             jobs[job_id]["message"] = "Using JK Bank Logic..."
             from jk_processor import convert_pdf_to_excel
             output_filename = f"{job_id}.xlsx"
             output_path = os.path.join(output_dir, output_filename)
             
             try:
                 convert_pdf_to_excel(file_path, output_path)
                 jobs[job_id]["status"] = "completed"
                 jobs[job_id]["progress"] = 100
                 jobs[job_id]["message"] = "Conversion complete"
                 jobs[job_id]["output_file"] = output_path
                 return
             except Exception as e:
                 raise ValueError(f"JK Bank Conversion Failed: {str(e)}")

        elif conversion_type == "rpt_pdf":
             jobs[job_id]["message"] = "Using RPT PDF Logic..."
             from rpt_pdf_processor import convert_rpt_pdf_to_excel
             output_filename = f"{job_id}.xlsx"
             output_path = os.path.join(output_dir, output_filename)
             
             try:
                 row_count = convert_rpt_pdf_to_excel(file_path, output_path)
                 jobs[job_id]["status"] = "completed"
                 jobs[job_id]["progress"] = 100
                 jobs[job_id]["message"] = f"Conversion complete: captured {row_count} transactions"
                 jobs[job_id]["output_file"] = output_path
                 return
             except Exception as e:
                 raise ValueError(f"RPT PDF Conversion Failed: {str(e)}")

        elif conversion_type == "rpt":
             jobs[job_id]["message"] = "Parsing RPT file..."
             df = parse_rpt_file(file_path)
             save_to_excel(df, job_id, jobs, output_dir)
             return

        else:
            # Generic / Auto-detect
            if ext == ".pdf":
                process_generic_pdf(file_path, job_id, jobs, output_dir)
                return
                            
            elif ext in [".jpg", ".jpeg", ".png"]:
                jobs[job_id]["message"] = "Processing image (OCR)..."
                text = pytesseract.image_to_string(Image.open(file_path))
                lines = text.split('\n')
                data = [line.split() for line in lines if line.strip()]
                df = pd.DataFrame(data)
                save_to_excel(df, job_id, jobs, output_dir)
                return
                
            elif ext == ".rpt":
                jobs[job_id]["message"] = "Parsing RPT file..."
                df = parse_rpt_file(file_path)
                save_to_excel(df, job_id, jobs, output_dir)
                return
    
            else:
                raise ValueError("Unsupported file format")

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = str(e)
        print(f"Error processing job {job_id}: {e}")

def process_generic_pdf(file_path, job_id, jobs, output_dir):
    all_rows = []
    
    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)
        
        # Step 1: Detect Columns (using first few pages)
        col_bounds = detect_pdf_columns(pdf.pages[:3])
        
        for i, page in enumerate(pdf.pages):
            if i % 5 == 0 or i == total_pages - 1:
                progress = 10 + int((i / total_pages) * 80)
                jobs[job_id]["progress"] = progress
                jobs[job_id]["message"] = f"Processing page {i+1} of {total_pages}"
            
            words = page.extract_words()
            if not words:
                continue
                
            # Group by line
            words.sort(key=lambda w: w['top'])
            lines = []
            current_line = []
            last_top = 0
            
            for word in words:
                if not current_line:
                    current_line.append(word)
                    last_top = word['top']
                else:
                    if abs(word['top'] - last_top) < 5: # Tolerance for same line
                        current_line.append(word)
                    else:
                        lines.append(current_line)
                        current_line = [word]
                        last_top = word['top']
            if current_line:
                lines.append(current_line)
            
            # Bucket words into columns
            for line_words in lines:
                row = [""] * (len(col_bounds) + 1)
                for word in line_words:
                    x = (word['x0'] + word['x1']) / 2
                    bucket = 0
                    for bound in col_bounds:
                        if x > bound:
                            bucket += 1
                        else:
                            break
                    row[bucket] += word['text'] + " "
                
                row = [c.strip() for c in row]
                if any(row):
                    all_rows.append(row)

    if not all_rows:
        raise ValueError("No text found in PDF")

    # Basic cleanup and Header detection
    df = pd.DataFrame(all_rows)
    # Filter out potential repeated headers if they are same as first row
    if len(df) > 1:
        header = df.iloc[0].tolist()
        # Simple heuristic: if a row is very similar to header, it's likely a repeated header
        # But we'll just keep everything for now and let user see.
        pass

    save_to_excel(df, job_id, jobs, output_dir)

def detect_pdf_columns(pages):
    """Detect vertical column boundaries by finding gaps in X-coordinates."""
    x_coords = []
    for page in pages:
        words = page.extract_words()
        for w in words:
            # Use midpoints to avoid being confused by slightly leaning text
            x_coords.append((w['x0'] + w['x1']) / 2)
    
    if not x_coords:
        return [100, 200, 300, 400] # Fallbacks
        
    x_coords.sort()
    
    # Find gaps
    gaps = []
    for i in range(len(x_coords) - 1):
        gap_size = x_coords[i+1] - x_coords[i]
        if gap_size > 15: # Threshold for a column gap
            gaps.append((gap_size, (x_coords[i] + x_coords[i+1]) / 2))
    
    gaps.sort(reverse=True)
    # Take top N gaps (likely column boundaries)
    # usually bank statements have 4-7 columns
    bounds = sorted([g[1] for g in gaps[:6]])
    return bounds

def save_to_excel(df, job_id, jobs, output_dir):
    output_filename = f"{job_id}.xlsx"
    output_path = os.path.join(output_dir, output_filename)
    
    df.to_excel(output_path, index=False, header=False) # Keep header=False as we might have headers in rows
    
    jobs[job_id]["status"] = "completed"
    jobs[job_id]["progress"] = 100
    jobs[job_id]["message"] = "Conversion complete"
    jobs[job_id]["output_file"] = output_path
