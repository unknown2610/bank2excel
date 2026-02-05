import pdfplumber
import pandas as pd
import re

pdf_path = "3010-41.pdf"
output_excel = "3010-41.xlsx"

# Phrases that indicate a line is NOT a valid transaction part
IGNORE_PHRASES = [
    "Transaction Details",
    "Printed By",
    "TO:",
    "M/S..",
    "CITY CHOWK",
    "POONCH",
    "cKYC Id",
    "No Nomination",
    "STATEMENT OF ACCOUNT",
    "DATE PARTICULARS",
    "Unless the constituent",
    "immediately of any discrepancy",
    "by him in this statement",
    "it will be taken that",
    "the account correct",
    "JAMMU AND KASHMIR BANK",
    "IFSC Code",
    "PHONE Code",
    "TYPE: CASH CREDIT",
    "A/C NO:",
    "https://",
    "Date Stamp Manager",
    "----------------"
]

def is_date(text):
    return bool(re.match(r'\d{2}-\d{2}-\d{4}', text))

def is_garbage(line_text):
    for phrase in IGNORE_PHRASES:
        if phrase in line_text:
            return True
    return False

def parse_pdf(pdf_path):
    """
    RPT IN PDF Logic:
    Takes items or particulars where a date is mentioned.
    If a row starts with a date at the extreme left, it's a new transaction.
    Does NOT stop at 'Page Total' - captures everything with a valid transaction pattern.
    """
    transactions = []
    current_tx = None 
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Processing {total_pages} pages using 'RPT IN PDF' logic...")
        
        for i, page in enumerate(pdf.pages):
            words = page.extract_words()
            # Sort order: top, then x0
            words.sort(key=lambda w: (round(w['top']), w['x0']))
            
            # Group into lines - process ALL lines on the page
            lines = []
            if not words:
                continue
                
            current_line = [words[0]]
            for w in words[1:]:
                if abs(w['top'] - current_line[-1]['top']) < 5:
                    current_line.append(w)
                else:
                    lines.append(current_line)
                    current_line = [w]
            if current_line:
                lines.append(current_line)

            for line in lines:
                line_text = " ".join([w['text'] for w in line])
                
                # Still use is_garbage to filter clear header/noise text
                if is_garbage(line_text):
                    continue

                # Detect New Transaction based on Date at Extreme Left
                first_word = line[0]
                has_date = False
                
                is_bf = "B/F" in line_text and "Balance" not in line_text
                
                # RPT IN PDF Rule: Date is always on the Extreme left side
                # Based on analysis, date x0 is approx 65. Header labels are usually 100+.
                if (first_word['x0'] < 100 and is_date(first_word['text'])) or (is_bf and first_word['x0'] < 180):
                    has_date = True
                
                if has_date:
                    if current_tx:
                        transactions.append(current_tx)
                    
                    current_tx = {
                        "DATE": first_word['text'] if not is_bf else "B/F",
                        "PARTICULARS": "",
                        "CHQ/REF": "",
                        "WITHDRAWALS": "",
                        "DEPOSITS": "",
                        "BALANCE": ""
                    }
                    start_idx = 1 if is_date(first_word['text']) else 0
                    process_line_content(line[start_idx:], current_tx)
                    
                else:
                    # Continue building current transaction
                    if current_tx:
                        process_line_content(line, current_tx)
        
        # After all pages, save the last transaction
        if current_tx:
            transactions.append(current_tx)
            print(f"  Final: Saved last transaction {current_tx['DATE']}")

    return transactions

def process_line_content(line_words, tx):
    # Updated Coords based on analysis:
    # DATE: x0 ≈ 65
    # PARTICULARS: x0 ≈ 132
    # CHQ/REF: (Usually merged or in particulars, but we'll try to pick it up if it exists)
    # WITHDRAWALS: x0 ≈ 344-350
    # DEPOSITS: (Need to check if any exist, but coordinates usually follow after withdrawals)
    # BALANCE: x0 ≈ 489
    
    # Coords from analyze_3010_41.py:
    # DATE: 65.15
    # PARTICULARS: 132.10
    # WITHDRAWALS/DEPOSITS: 344.08, 349.66
    # BALANCE: 489.13

    for w in line_words:
        x = w['x0']
        text = w['text']
        
        if 120 <= x < 330:
             # Particulars often contain Ref Nos in this PDF layout
             tx["PARTICULARS"] += " " + text
        elif 330 <= x < 410:
             # This seems to be the withdrawal column area
             tx["WITHDRAWALS"] += text
        elif 410 <= x < 480:
             # This seems to be the deposit column area
             tx["DEPOSITS"] += text
        elif x >= 480:
             tx["BALANCE"] += text
            
    # Cleanup strings
    tx["PARTICULARS"] = tx["PARTICULARS"].strip()

def save_to_excel(transactions, output_filename):
    df = pd.DataFrame(transactions)
    
    # Clean Numeric Columns
    for col in ["WITHDRAWALS", "DEPOSITS", "BALANCE"]:
        if col in df.columns:
            # Remove Cr/Dr markers and commas
            df[col] = df[col].astype(str).str.replace(r'Cr', '', regex=False).str.replace(r'Dr', '', regex=False).str.replace(r',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df.to_excel(output_filename, index=False)
    print(f"\nSaved {len(df)} transactions to {output_filename}")

if __name__ == "__main__":
    data = parse_pdf(pdf_path)
    save_to_excel(data, output_excel)
