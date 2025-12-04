import re
import pandas as pd

def parse_rpt_file(file_path):
    """
    Parses a fixed-width .rpt bank statement file.
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # 1. Find Header Line and Determine Column Positions
    header_line_idx = -1
    header_indices = {}
    
    # Keywords to identify the header line
    # Based on user image: DATE, PARTICULARS, CHQ.NO./REF.NO., WITHDRAWALS, DEPOSITS, BALANCE
    keywords = ["DATE", "PARTICULARS", "CHQ.NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"]
    
    for i, line in enumerate(lines):
        # Check if enough keywords are present to confirm it's the header
        if "DATE" in line and "PARTICULARS" in line and "BALANCE" in line:
            header_line_idx = i
            
            # Find start positions of each column
            # We add a small buffer or rely on the visual spacing. 
            # Using .find() gives the start index.
            p_date = line.find("DATE")
            p_part = line.find("PARTICULARS")
            p_chq = line.find("CHQ.NO") 
            if p_chq == -1: p_chq = line.find("REF.NO") # Fallback
            
            p_with = line.find("WITHDRAWALS")
            p_dep = line.find("DEPOSITS")
            p_bal = line.find("BALANCE")
            
            # Handle missing columns if any (though unlikely for this format)
            # We assume the order: DATE | PARTICULARS | CHQ | WITH | DEP | BAL
            
            # Define slice ranges
            # We'll use the start of the next column as the end of the current one
            # For the last column, we go to the end of the line
            
            header_indices = {
                "date": (0, p_part), 
                "particulars": (p_part, p_chq),
                "cheque": (p_chq, p_with),
                "withdrawals": (p_with, p_dep),
                "deposits": (p_dep, p_bal),
                "balance": (p_bal, None)
            }
            break
            
    if header_line_idx == -1:
        # Fallback: If no header found, maybe try to guess or return empty
        # For now, let's assume the format matches the user's request
        print("Warning: Header not found. Attempting to parse with default offsets or failing.")
        # We could try default offsets if we knew them, but for now let's error out or return empty
        return pd.DataFrame()

    data = []
    current_row = None
    
    # Regex for date validation (DD-MM-YYYY)
    # The image shows 08-04-2024, so \d{2}-\d{2}-\d{4}
    date_pattern = re.compile(r'^\d{2}-\d{2}-\d{4}')

    for line in lines[header_line_idx+1:]:
        stripped_line = line.strip()
        if not stripped_line: continue
        if stripped_line.startswith("-------"): continue # Separator lines
        if "Page Total:" in line: continue # Footer
        if "Opening Balance" in line: continue # Sometimes appears
        
        # Helper to extract fixed-width field
        def get_field(start, end):
            if start == -1: return ""
            # If end is None, go to end of string
            val = line[start:end].strip() if end is not None else line[start:].strip()
            return val

        # Extract raw fields
        date_val = get_field(*header_indices["date"])
        part_val = get_field(*header_indices["particulars"])
        chq_val = get_field(*header_indices["cheque"])
        with_val = get_field(*header_indices["withdrawals"])
        dep_val = get_field(*header_indices["deposits"])
        bal_val = get_field(*header_indices["balance"])

        # Check if this line starts a new transaction
        if date_pattern.match(date_val):
            # Save the previous row if it exists
            if current_row:
                data.append(current_row)
            
            # Initialize new row
            current_row = {
                "Date": date_val,
                "Particulars": part_val,
                "Cheque No": chq_val,
                "Withdrawals": with_val,
                "Deposits": dep_val,
                "Balance": bal_val
            }
        else:
            # It's a continuation line (or a line without a date)
            if current_row:
                # Append Particulars text if present
                if part_val:
                    current_row["Particulars"] += " " + part_val
                
                # Update other fields if they were empty in the main row but present here
                # Or if they are just split across lines (like the amounts in the example)
                if chq_val: current_row["Cheque No"] = chq_val
                if with_val: current_row["Withdrawals"] = with_val
                if dep_val: current_row["Deposits"] = dep_val
                if bal_val: current_row["Balance"] = bal_val

    # Don't forget the last row
    if current_row:
        data.append(current_row)
        
    df = pd.DataFrame(data)
    return df
