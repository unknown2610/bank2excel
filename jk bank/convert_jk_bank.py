import pdfplumber
import pandas as pd
import re

def convert_pdf_to_excel(pdf_path, excel_path):
    print(f"Processing {pdf_path}...")
    
    all_rows = []
    
    # Define Column Boundaries (X-coords)
    # Date < 120
    # 120 < Part < 460
    # 460 < With < 580
    # 580 < Dep < 690
    # 690 < Bal
    COL_BOUNDS = [120, 460, 580, 690]
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            
            # Group words by line (vertical alignment)
            # Sort by 'top' first
            words.sort(key=lambda w: w['top'])
            
            lines = []
            current_line = []
            last_top = 0
            
            for word in words:
                if not current_line:
                    current_line.append(word)
                    last_top = word['top']
                else:
                    # Check if on same line (tolerance 10px to handle slight misalignments)
                    if abs(word['top'] - last_top) < 10:
                        current_line.append(word)
                    else:
                        lines.append(current_line)
                        current_line = [word]
                        last_top = word['top']
            if current_line:
                lines.append(current_line)
            
            # Process each line
            for line_words in lines:
                # 5 Buckets
                cols = ["", "", "", "", ""]
                
                for word in line_words:
                    x = word['x0']
                    text = word['text']
                    
                    # Assign to bucket
                    if x < COL_BOUNDS[0]: # Date
                        cols[0] += text + " "
                    elif x < COL_BOUNDS[1]: # Particulars
                        cols[1] += text + " "
                    elif x < COL_BOUNDS[2]: # Withdrawals
                        cols[2] += text + " "
                    elif x < COL_BOUNDS[3]: # Deposits
                        cols[3] += text + " "
                    else: # Balance
                        cols[4] += text + " "
                
                # Strip spaces
                cols = [c.strip() for c in cols]
                
                # Filter headers
                if "Date" in cols[0] and "Particulars" in cols[1]:
                    continue
                
                # Filter empty rows (ignore strictly empty)
                if not any(cols):
                    continue

                all_rows.append(cols)

    print(f"DEBUG: First 20 raw rows:")
    for i, r in enumerate(all_rows[:20]):
        print(f"Row {i}: {r}")

    # Post-processing
    def clean_currency(val):
        if not val:
            return 0.0
        # Remove chars that are not digits or dot or minus
        # Keep it simple: remove spaces and commas
        clean_val = val.replace(" ", "").replace(",", "")
        try:
            return float(clean_val)
        except ValueError:
            return 0.0 # Or return val if we want to debug text leakage

    cleaned_rows = []
    current_row = None

    for row in all_rows:
        date_col = row[0]
        part_col = row[1]
        with_col = clean_currency(row[2])
        dep_col = clean_currency(row[3])
        bal_col = clean_currency(row[4])

        # New Txn Logic
        is_new_txn = False
        # Regex for date
        if re.search(r'\d{1,2}[-.\s][A-Za-z]{3}[-.\s]\d{4}', date_col):
            is_new_txn = True
        
        # Opening Balance Case
        if "Opening Balance" in part_col:
             # Handle Opening Balance explicitly
             cleaned_rows.append(["", "Opening Balance", 0.0, 0.0, float(bal_col or with_col or dep_col or 0)]) 
             # Note: Opening balance might end up in a wrong column if logic is weird, but usually it's in Bal.
             # Wait, row 1 example: Open Bal was part_col, and Amount was... where?
             # In debug Row 1: `..., '5,030.18'` -> it was in last column?
             # Our bucket logic will place it in last column if x > 690.
             continue

        if is_new_txn:
            if current_row:
                cleaned_rows.append(current_row)
            current_row = [date_col, part_col, with_col, dep_col, bal_col]
        else:
            if current_row:
                if part_col:
                    current_row[1] += " " + part_col
                # If numbers appear on continuation lines, accumulating them is risky?
                # Usually they shouldn't.
                # If they do, maybe check if current_row has 0?
                # For safety, let's just merge text.
    
    if current_row:
        cleaned_rows.append(current_row)

    df = pd.DataFrame(cleaned_rows, columns=["Date", "Particulars", "Withdrawals", "Deposits", "Balance"])
    excel_file = "JK_Bank_Statement_v3.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"Saved to {excel_path} with {len(df)} rows.")

if __name__ == "__main__":
    pdf_file = "AccountStmt_1761195605574.pdf"
    excel_file = "JK_Bank_Statement_fixed.xlsx"
    convert_pdf_to_excel(pdf_file, excel_file)
