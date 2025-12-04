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
    
    for i, line in enumerate(lines):
        if "DATE" in line and "PARTICULARS" in line and "BALANCE" in line:
            header_line_idx = i
            
            # Use specific logic for Date and Particulars split
            # Date is always DD-MM-YYYY (10 chars). We'll assume a safe gap.
            # But for the rest, we use the header positions.
            
            p_chq = line.find("CHQ.NO") 
            if p_chq == -1: p_chq = line.find("REF.NO")
            
            p_with = line.find("WITHDRAWALS")
            p_dep = line.find("DEPOSITS")
            p_bal = line.find("BALANCE")
            
            # Define slice ranges based on header
            # We will handle Date/Particulars split dynamically in the loop
            header_indices = {
                "cheque_start": p_chq,
                "with_start": p_with,
                "dep_start": p_dep,
                "bal_start": p_bal
            }
            break
            
    if header_line_idx == -1:
        return pd.DataFrame()

    data = []
    current_row = None
    date_pattern = re.compile(r'^\d{2}-\d{2}-\d{4}')

    for line in lines[header_line_idx+1:]:
        if not line.strip(): continue
        if line.strip().startswith("-------"): continue
        if "Page Total:" in line: continue
        
        # 1. Extract Date (Fixed width 10 chars + buffer)
        # We assume Date is at the very beginning of the line
        possible_date = line[:10].strip()
        is_new_row = date_pattern.match(possible_date)
        
        # 2. Extract other fixed columns based on header positions
        # We need to be careful: The header positions are starting points.
        # Particulars ends where Cheque starts.
        
        idx_chq = header_indices["cheque_start"]
        idx_with = header_indices["with_start"]
        idx_dep = header_indices["dep_start"]
        idx_bal = header_indices["bal_start"]
        
        # Helper to safely slice
        def get_slice(s, start, end):
            if start >= len(s): return ""
            return s[start:end].strip()

        # Date is first 10 chars. Particulars is from 10 to idx_chq.
        # But we need to handle the case where Particulars bleeds left or right.
        # The user said "08-04-2024 M" was in A. That means we took too much for A.
        # We will strictly take 10 chars for date.
        
        date_val = line[:10].strip() if is_new_row else ""
        
        # Particulars: from index 11 (skip space) to Cheque Start
        # We give a small buffer of 1-2 chars for the gap
        part_val = get_slice(line, 11, idx_chq)
        
        chq_val = get_slice(line, idx_chq, idx_with)
        with_val = get_slice(line, idx_with, idx_dep)
        dep_val = get_slice(line, idx_dep, idx_bal)
        bal_val = get_slice(line, idx_bal, None)

        # CLEANING: Remove "INR" from Cheque No
        if "INR" in chq_val:
            chq_val = chq_val.replace("INR", "").strip()
            # If it was ONLY an amount (like 269.00), it might be empty now or just a number
            # The user said "no INR amount".
            # If it looks like a float, and we have a value in Withdrawals/Deposits, it's likely redundant.
            try:
                float(chq_val)
                # It is a number. Is it a cheque number or an amount?
                # Cheque numbers are usually integers. Amounts have decimals.
                if "." in chq_val:
                    chq_val = "" # Assume it's a misplaced amount
            except ValueError:
                pass # It's alphanumeric, likely a real ref/cheque

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
                if chq_val: current_row["Cheque No"] = chq_val # Overwrite or append? Usually overwrite if empty
                if with_val: current_row["Withdrawals"] = with_val
                if dep_val: current_row["Deposits"] = dep_val
                if bal_val: current_row["Balance"] = bal_val

    if current_row:
        data.append(current_row)
        
    # Explicitly define columns to avoid KeyError if data is empty
    columns = ["Date", "Particulars", "Cheque No", "Withdrawals", "Deposits", "Balance"]
    df = pd.DataFrame(data, columns=columns)
    
    if df.empty:
        return df

    # POST-PROCESSING: Convert types for Excel
    # We need to return the DF, but the formatting happens at save time.
    # However, we can convert columns to numeric here so pandas knows they are numbers.
    
    def clean_currency(x):
        if not x: return None
        # Remove 'Cr', 'Dr', 'INR', commas
        x = str(x).upper().replace("CR", "").replace("DR", "").replace("INR", "").replace(",", "").strip()
        try:
            return float(x)
        except ValueError:
            return None

    df["Withdrawals"] = df["Withdrawals"].apply(clean_currency)
    df["Deposits"] = df["Deposits"].apply(clean_currency)
    df["Balance"] = df["Balance"].apply(clean_currency)
    
    return df
