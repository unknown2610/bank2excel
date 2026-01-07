import pandas as pd

def verify_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        print(f"File loaded successfully. Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head().to_string())
        
        # Check specific values from Row 5 (Index 2 in dataframe if row 0 is header)
        # Expected: Date: 03-04-2025, Particulars: IMPS..., Withdrawal: 8000
        print("\nRow check (Index 2):")
        print(df.iloc[2].to_string())
        
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    verify_excel(r"c:\Users\gurpr\.gemini\antigravity\AI PROJECTS\rpt converter\output_v2.xlsx")
