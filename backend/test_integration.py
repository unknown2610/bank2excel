import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from processor import process_bank_statement

# Mock jobs dictionary
jobs = {
    "test_job": {
        "status": "pending",
        "progress": 0,
        "message": "Queued"
    }
}

# Path to our test PDF (relative to backend dir)
pdf_path = "../../rpt in pdf/3010-41.pdf"
output_dir = "outputs"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"--- Testing RPT PDF Integration ---")
process_bank_statement(pdf_path, "test_job", jobs, output_dir, conversion_type="rpt_pdf")

print(f"\nResult:")
print(f"Status: {jobs['test_job']['status']}")
print(f"Message: {jobs['test_job']['message']}")
if "output_file" in jobs['test_job']:
    print(f"Output: {jobs['test_job']['output_file']}")
    if os.path.exists(jobs['test_job']['output_file']):
        print("Verification: SUCCESS (Excel file created)")
    else:
        print("Verification: FAILED (Excel file not found)")
else:
    print("Verification: FAILED (No output file in job status)")
