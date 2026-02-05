import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from processor import process_bank_statement
import pandas as pd

# Mock jobs and results
jobs = {
    "test_job": {
        "status": "pending",
        "progress": 0,
        "message": ""
    }
}
OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

test_pdf = r"c:\Users\gurpr\.gemini\antigravity\AI PROJECTS\Bank2Excel\jk bank\AccountStmt_1761195605574.pdf"

print(f"Testing Generic PDF Extraction with: {test_pdf}")

try:
    process_bank_statement(test_pdf, "test_job", jobs, OUTPUT_DIR, conversion_type="generic")
    
    if jobs["test_job"]["status"] == "completed":
        print("SUCCESS: Conversion completed.")
        output_file = jobs["test_job"]["output_file"]
        print(f"Output saved to: {output_file}")
        
        # Load and check
        df = pd.read_excel(output_file)
        print("\nExtracted Data Preview (First 5 rows):")
        print(df.head())
        
        if len(df) > 0:
            print(f"\nTotal rows extracted: {len(df)}")
            print("SUCCESS: Data found in Excel.")
        else:
            print("FAILURE: No data in Excel.")
    else:
        print(f"FAILURE: Job status is {jobs['test_job']['status']}")
        print(f"Message: {jobs['test_job']['message']}")

except Exception as e:
    print(f"Error during test: {e}")
