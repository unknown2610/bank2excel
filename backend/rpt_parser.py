import pandas as pd
import re
import os

def parse_rpt_file(file_path):
    transactions = []
    current_tx = None
    
    # Default Indices (Fallback)
    col_indices = {
        'Date': (0, 11),
        'Particulars': (11, 45),
        'Chq/Ref No.': (45, 65),
        'Withdrawals': (65, 85),
        'Deposits': (85, 105),
        'Balance': (105, None)
    }

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Column markers to help dynamic detection
    markers = {
        'DATE': 'Date',
        'PARTICULARS': 'Particulars',
        'CHQ.NO': 'Chq/Ref No.',
        'WITHDRAWALS': 'Withdrawals',
        'DEPOSITS': 'Deposits',
        'BALANCE': 'Balance'
    }

    date_pattern = re.compile(r'\d{2}-\d{2}-\d{4}')

    # Better Dynamic Detection
    for line in lines[:20]:
        if sum(1 for m in markers if m in line) >= 3:
            all_found_markers = {m: line.find(m) for m in markers if line.find(m) != -1}
            sorted_markers = sorted([(pos, m) for m, pos in all_found_markers.items()])
            
            new_indices = {}
            for i in range(len(sorted_markers)):
                start_pos, marker = sorted_markers[i]
                col_name = markers[marker]
                
                # col_start
                if i == 0:
                    col_start = 0
                else:
                    prev_end = sorted_markers[i-1][0] + len(sorted_markers[i-1][1])
                    col_start = (prev_end + start_pos) // 2
                    
                # col_end
                if i == len(sorted_markers) - 1:
                    col_end = None
                else:
                    this_end = start_pos + len(marker)
                    next_start = sorted_markers[i+1][0]
                    col_end = (this_end + next_start) // 2
                
                new_indices[col_name] = (col_start, col_end)
            
            # Refine Date/Particulars boundary if Date detected at start
            if 'Date' in new_indices and new_indices['Date'][0] == 0:
                # Look for a date in the next few lines to see its actual end
                for next_line in lines[lines.index(line)+1 : lines.index(line)+10]:
                    match = date_pattern.search(next_line)
                    if match:
                        date_end = match.end()
                        # Date column should end slightly after the date match
                        new_indices['Date'] = (0, date_end + 1)
                        if 'Particulars' in new_indices:
                             ps, pe = new_indices['Particulars']
                             new_indices['Particulars'] = (date_end + 1, pe)
                        break
            
            col_indices.update(new_indices)
            break

    for line in lines:
        if not line.strip():
            continue
            
        def get_field(col_name):
            if col_name not in col_indices:
                 return ""
            start, end = col_indices[col_name]
            val = line[start:end].strip() if end else line[start:].strip()
            return val

        date_str = get_field('Date')
        particulars = get_field('Particulars')
        chq_no = get_field('Chq/Ref No.')
        withdrawal_str = get_field('Withdrawals')
        deposit_str = get_field('Deposits')
        balance_str = get_field('Balance')

        if sum(1 for m in markers if m in line) >= 3:
            continue

        if date_pattern.match(date_str):
            if current_tx:
                transactions.append(current_tx)
            
            current_tx = {
                'Date': date_str,
                'Particulars': particulars,
                'Chq/Ref No.': chq_no,
                'Withdrawals': parse_amount(withdrawal_str),
                'Deposits': parse_amount(deposit_str),
                'Balance': parse_amount(balance_str)
            }
        else:
            if current_tx:
                if particulars:
                    current_tx['Particulars'] += " " + particulars
                if chq_no:
                    if not current_tx['Chq/Ref No.']:
                        current_tx['Chq/Ref No.'] = chq_no
                    else:
                        current_tx['Chq/Ref No.'] += " " + chq_no
                        
                if withdrawal_str:
                    amount = parse_amount(withdrawal_str)
                    if amount != 0.0:
                        current_tx['Withdrawals'] += amount

                if deposit_str:
                    amount = parse_amount(deposit_str)
                    if amount != 0.0:
                        current_tx['Deposits'] += amount
                            
                if balance_str:
                    # Update balance (usually the last line of a txn has the correct running balance)
                    current_tx['Balance'] = parse_amount(balance_str)

    if current_tx:
        transactions.append(current_tx)

    df = pd.DataFrame(transactions)
    columns = ['Date', 'Particulars', 'Chq/Ref No.', 'Withdrawals', 'Deposits', 'Balance']
    df = df[columns] if not df.empty else pd.DataFrame(columns=columns)
    
    if not df.empty:
        df['Particulars'] = df['Particulars'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip() if x else "")
        df['Chq/Ref No.'] = df['Chq/Ref No.'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip() if x else "")

    return df

def parse_amount(amount_str):
    if not amount_str:
        return 0.0
    try:
        # Robust parsing: remove everything except digits, dots and minus
        # Handle Dr/Cr by checking for 'Dr' or 'Cr'
        is_dr = 'Dr' in str(amount_str)
        is_cr = 'Cr' in str(amount_str)
        
        clean_val = re.sub(r'[^\d.-]', '', str(amount_str))
        if not clean_val or clean_val == "." or clean_val == "-":
            return 0.0
        
        val = float(clean_val)
        # Note: In bank statements, Dr usually means negative balance (overdraft) or withdrawal.
        # But we'll just keep it positive and let the user decide. 
        # Actually, let's keep it as is for now.
        return val
    except ValueError:
        return 0.0
