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
        "date_start": 0,
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
            p_date = line_upper.find("DATE")
            if p_date == -1: p_date = 0
            
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
                "date_start": p_date,
                "cheque_start": p_chq,
                "with_start": p_with,
                "dep_start": p_dep,
                "bal_start": p_bal
            }
            break
            
    data = []
    current_row = None
    
    # Regex for date validation (DD-MM-YYYY)
    date_pattern = re.compile(r'\d{2}-\d{2}-\d{4}')

    start_idx = header_line_idx + 1 if header_found else 0

    for line in lines[start_idx:]:
        if not line.strip(): continue
        if line.strip().startswith("-------"): continue
        if "Page Total:" in line: continue
        
        # 1. Extract Date
        # Use a wider window to find the date, handling potential margins
        # We look at the first 25 chars.
        date_window = line[:25]
        date_match = date_pattern.search(date_window)
        
        is_new_row = bool(date_match)
        date_val = date_match.group(0) if is_new_row else ""
        
        # 2. Extract columns
        # We use the header indices, but we need to be careful about the Date/Particulars split.
        # Particulars usually starts after Date.
        
        idx_date = header_indices["date_start"]
        idx_chq = header_indices["cheque_start"]
        idx_with = header_indices["with_start"]
        idx_dep = header_indices["dep_start"]
        idx_bal = header_indices["bal_start"]
        
        def get_slice(s, start, end):
            if start >= len(s): return ""
            return s[start:end].strip()

        # Particulars starts after date (approx 10-12 chars after date start)
        # Or we can use the header index of "PARTICULARS" if we had it.
        # Let's assume it starts 12 chars after date_start to be safe.
        part_start = idx_date + 11 
        
        part_val = get_slice(line, part_start, idx_chq)
        chq_val = get_slice(line, idx_chq, idx_with)
        with_val = get_slice(line, idx_with, idx_dep)
        dep_val = get_slice(line, idx_dep, idx_bal)
        bal_val = get_slice(line, idx_bal, None)

        # CLEANING
        if "INR" in chq_val:
            chq_val = chq_val.replace("INR", "").strip()
        
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
    def parse_date(x):
        try:
            return pd.to_datetime(x, format="%d-%m-%Y").date()
        except:
            return x
            
    df["Date"] = df["Date"].apply(parse_date)

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
