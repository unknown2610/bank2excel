import re
import pandas as pd
from datetime import datetime

def parse_rpt_file(file_path):
    """
    Parses a fixed-width .rpt bank statement file.
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Default indices based on the known format (fallback)
    header_indices = {
        "cheque_start": 50, 
        "with_start": 70,
        "dep_start": 90,
        "bal_start": 110
    }
    
    header_found = False
    header_line_idx = -1
    
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if "DATE" in line_upper and "PARTICULARS" in line_upper:
            header_line_idx = i
            header_found = True
            
            # Dynamic positions
            p_chq = line_upper.find("CHQ.NO") 
            if p_chq == -1: p_chq = line_upper.find("REF.NO")
            if p_chq == -1: p_chq = 45 # Fallback
            
            p_with = line_upper.find("WITHDRAWALS")
            if p_with == -1: p_with = 65
            
            p_dep = line_upper.find("DEPOSITS")
            if p_dep == -1: p_dep = 85
            
            p_bal = line_upper.find("BALANCE")
            if p_bal == -1: p_bal = 105
            
            header_indices = {
                "cheque_start": p_chq,
                "with_start": p_with,
                "dep_start": p_dep,
                "bal_start": p_bal
            }
            break
            
    data = []
    current_row = None
    
    # Regex for date validation (DD-MM-YYYY)
    date_pattern = re.compile(r'^\d{2}-\d{2}-\d{4}')

    start_idx = header_line_idx + 1 if header_found else 0

    for line in lines[start_idx:]:
        if not line.strip(): continue
        if line.strip().startswith("-------"): continue
        if "Page Total:" in line: continue
        
        # 1. Extract Date (Fixed width 10 chars)
        # We assume Date is at the very beginning of the line
        possible_date = line[:10].strip()
        is_new_row = bool(date_pattern.match(possible_date))
        
        # 2. Extract columns
        idx_chq = header_indices["cheque_start"]
        idx_with = header_indices["with_start"]
        idx_dep = header_indices["dep_start"]
        idx_bal = header_indices["bal_start"]
        
        def get_slice(s, start, end):
            if start >= len(s): return ""
            return s[start:end].strip()

        date_val = line[:10].strip() if is_new_row else ""
        
        # Particulars: strictly start after the date column (index 10)
        # We skip index 10 (usually a space) and start at 11.
        # If the file is jammed, we might need to check line[10]
        part_start = 11
        if len(line) > 10 and line[10] != ' ':
             # If no space, maybe it's jammed? But standard is 10 chars for date.
             # We will stick to 11 to avoid taking the last char of date if date was somehow longer (unlikely)
             pass

        part_val = get_slice(line, part_start, idx_chq)
        chq_val = get_slice(line, idx_chq, idx_with)
        with_val = get_slice(line, idx_with, idx_dep)
        dep_val = get_slice(line, idx_dep, idx_bal)
        bal_val = get_slice(line, idx_bal, None)

        # CLEANING
        if "INR" in chq_val:
            chq_val = chq_val.replace("INR", "").strip()
        
        # Remove standalone amounts from Cheque column
        # If it looks like a float (has a dot), it's probably an amount
        try:
            if chq_val and "." in chq_val:
                float(chq_val)
                chq_val = "" 
        except ValueError:
            pass

        if is_new_row:
            if current_row:
                data.append(current_row)
            
            current_row = {
                "Date": date_val,
                "Particulars": part_val,
                "Cheque No": chq_val,
                "Withdrawals": with_val,
                "Deposits": dep_val,
                "Balance": bal_val
            }
        else:
            # Continuation
            if current_row:
                if part_val: current_row["Particulars"] += " " + part_val
                if chq_val: current_row["Cheque No"] = chq_val 
                if with_val: current_row["Withdrawals"] = with_val
                if dep_val: current_row["Deposits"] = dep_val
                if bal_val: current_row["Balance"] = bal_val

    if current_row:
        data.append(current_row)
        
    columns = ["Date", "Particulars", "Cheque No", "Withdrawals", "Deposits", "Balance"]
    df = pd.DataFrame(data, columns=columns)
    
    if df.empty:
        return df

    # POST-PROCESSING
    
    # 1. Convert Date to datetime objects for Excel formatting
    def parse_date(x):
        try:
            return pd.to_datetime(x, format="%d-%m-%Y").date()
        except:
            return x
            
    df["Date"] = df["Date"].apply(parse_date)

    # 2. Convert Numbers
    def clean_currency(x):
        if not x: return None
        x = str(x).upper().replace("CR", "").replace("DR", "").replace("INR", "").replace(",", "").strip()
        try:
            return float(x)
        except ValueError:
            return None

    df["Withdrawals"] = df["Withdrawals"].apply(clean_currency)
    df["Deposits"] = df["Deposits"].apply(clean_currency)
    df["Balance"] = df["Balance"].apply(clean_currency)
    
    return df
