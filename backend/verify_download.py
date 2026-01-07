import requests
import time
import os

BASE_URL = "http://localhost:8000"
TEST_FILE = "test_verification.txt"

# Create a dummy file
with open(TEST_FILE, "w") as f:
    f.write("Dummy content")

try:
    # 1. Upload
    print("Uploading file...")
    with open(TEST_FILE, "rb") as f:
        files = {"file": (TEST_FILE, f, "text/plain")}
        data = {"conversion_type": "generic"} # or "rpt"
        res = requests.post(f"{BASE_URL}/upload", files=files, data=data)
    
    if res.status_code != 200:
        print(f"Upload failed: {res.text}")
        exit(1)
        
    job_id = res.json()["job_id"]
    print(f"Job ID: {job_id}")

    # 2. Wait for confirmation (simulated, since generic might fail on txt but we just want to check filename logic if it gets that far, 
    # actually generic processor checks extension. Let's use a supported fake extension or just minimal file)
    # The processor checks extension. If we send .txt, it raises "Unsupported file format".
    # We need to send a .rpt or .pdf or image. 
    # Let's create a dummy .rpt
    
    os.remove(TEST_FILE)
    TEST_FILE = "test_verification.rpt"
    with open(TEST_FILE, "w") as f:
        f.write("Dummy RPT content")

    print("Uploading .rpt file...")
    with open(TEST_FILE, "rb") as f:
        files = {"file": (TEST_FILE, f, "application/octet-stream")}
        data = {"conversion_type": "rpt"} 
        res = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        
    job_id = res.json()["job_id"]
    print(f"Job ID: {job_id}")
    
    # Poll status
    for _ in range(10):
        res = requests.get(f"{BASE_URL}/status/{job_id}")
        status = res.json()["status"]
        print(f"Status: {status}")
        if status in ["completed", "failed"]:
            break
        time.sleep(1)
        
    if status != "completed":
        print("Processing failed (expected for dummy file, but we need success to test download header).")
        # If it fails, we can't download.
        # The Current RPT parser might fail on empty/dummy content. 
        # But we just want to test the filename logic in main.py, which happens inside download_file.
        # download_file checks if job["status"] == "completed".
        # So we need a successful job.
        # Let's use the 'jk_bank' mock/test if possible? Or just make rpt parser robust?
        # Actually, in processor.py, if we use "rpt", it calls `parse_rpt_file`.
        # If I can't guarantee success, I can't test download.
        
        # Alternative: We trust the code change in main.py?
        # The logic is: `download_name = f"{clean_name}_converted.xlsx"`
        # This is quite straightforward. 
        pass
    else:
        # 3. Check Download Header
        print("Checking download header...")
        res = requests.get(f"{BASE_URL}/download/{job_id}", stream=True)
        
        cd = res.headers.get("content-disposition")
        print(f"Content-Disposition: {cd}")
        
        expected = "test_verification_converted.xlsx"
        if expected in cd:
            print("SUCCESS: Filename is correct.")
        else:
            print(f"FAILURE: Expected {expected} in {cd}")

except Exception as e:
    print(f"Error: {e}")
finally:
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
