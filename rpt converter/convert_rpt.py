import pandas as pd
import re
import os

def parse_rpt(file_path):
    transactions = []
    current_tx = None
    
    # Column Indices (Refined)
    # Date: 2-12
    # Particulars: 14-33
    # Chq No: 33-51
    # Withdrawals: 51-64 (Previously 51-67)
    # Deposits: 64-79 (Previously 67-81)
    # Balance: 79-end (Previously 81-end)

    
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Skip header (Line 0)
    # Check for Opening Balance in Line 1?
    # We will process line by line.
    
    date_pattern = re.compile(r'\d{2}-\d{2}-\d{4}')

    for line in lines:
        # Skip empty lines or separator lines if any (though file looks clean)
        if not line.strip():
            continue
            
        # Extract fields
        date_str = line[2:12].strip()
        particulars = line[14:33].strip()
        chq_no = line[33:51].strip()
        withdrawal_str = line[51:64].strip()
        deposit_str = line[64:79].strip()
        balance_str = line[79:].strip()

        # Check if header
        if "DATE" in line and "PARTICULARS" in line:
            continue

        # Check if new transaction (Date present)
        if date_pattern.match(date_str):
            # Save previous transaction if exists
            if current_tx:
                transactions.append(current_tx)
            
            # Start new transaction
            current_tx = {
                'Date': date_str,
                'Particulars': particulars,
                'Chq/Ref No.': chq_no,
                'Withdrawals': parse_amount(withdrawal_str),
                'Deposits': parse_amount(deposit_str),
                'Balance': balance_str  # Keep string for now to preserve Dr/Cr
            }
        else:
            # No date. Could be:
            # 1. Opening balance line (at start)
            # 2. Continuation of particulars for previous transaction
            # 3. Attributes for previous transaction (Chq number, amounts) appearing on 2nd line
            
            if current_tx is None:
                # Handle Opening Balance Case?
                # If we see a balance but no date/particulars, maybe capture it?
                # For now let's just ignore if it's strictly just correct data.
                if balance_str and not particulars and not withdrawal_str and not deposit_str:
                     # Treat as initial opening balance if we want, or just skip. 
                     # Let's create a dummy entry for Opening Balance if needed.
                     pass
            else:
                # Append/Update data to current_tx
                if particulars:
                    current_tx['Particulars'] += " " + particulars
                if chq_no:
                    # If chq_no wasn't there, add it. If it was, maybe append? Usually it replaces or is unique.
                    if not current_tx['Chq/Ref No.']:
                        current_tx['Chq/Ref No.'] = chq_no
                    else:
                        current_tx['Chq/Ref No.'] += " " + chq_no
                        
                if withdrawal_str:
                    # If amount was missing on first line, take it now. 
                    # If amount was present, this might be a split? But usually amount is on one line.
                    amount = parse_amount(withdrawal_str)
                    if current_tx['Withdrawals'] == 0.0:
                        current_tx['Withdrawals'] = amount
                    else:
                        # Only add if it's non-zero
                         if amount != 0.0:
                            current_tx['Withdrawals'] += amount

                if deposit_str:
                    amount = parse_amount(deposit_str)
                    if current_tx['Deposits'] == 0.0:
                        current_tx['Deposits'] = amount
                    else:
                         if amount != 0.0:
                            current_tx['Deposits'] += amount
                            
                if balance_str:
                    # Update balance to the latest line's balance (usually the bottom line has the final balance for that tx)
                    current_tx['Balance'] = balance_str

    # Append last transaction
    if current_tx:
        transactions.append(current_tx)

    return transactions

def parse_amount(amount_str):
    if not amount_str:
        return 0.0
    try:
        # Remove commas if any (though typical RPT usually doesn't have them, python float handles plain nums)
        return float(amount_str.replace(',', ''))
    except ValueError:
        return 0.0

def convert_to_excel(input_path, output_path):
    data = parse_rpt(input_path)
    df = pd.DataFrame(data)
    
    # Reorder/Ensure columns
    columns = ['Date', 'Particulars', 'Chq/Ref No.', 'Withdrawals', 'Deposits', 'Balance']
    # Filter only columns that exist (in case no data found)
    df = df[columns] if not df.empty else pd.DataFrame(columns=columns)
    
    # Clean Particulars (remove double spaces)
    if not df.empty:
        df['Particulars'] = df['Particulars'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())
        df['Chq/Ref No.'] = df['Chq/Ref No.'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())

    df.to_excel(output_path, index=False)
    print(f"Successfully converted {input_path} to {output_path}")

if __name__ == "__main__":
    input_file = r"c:\Users\gurpr\.gemini\antigravity\AI PROJECTS\rpt converter\TMPDAAmL1n_dT12.RPT"
    output_file = r"c:\Users\gurpr\.gemini\antigravity\AI PROJECTS\rpt converter\output_v2.xlsx"
    convert_to_excel(input_file, output_file)
