
def check_indices(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    # Check Header (Line 0)
    header = lines[0]
    print(f"Header: {header.rstrip()}")
    print("Indices:")
    print(f"DATE: {header.find('DATE')}")
    print(f"PARTICULARS: {header.find('PARTICULARS')}")
    print(f"CHQ: {header.find('CHQ')}")
    print(f"WITHDRAWALS: {header.find('WITHDRAWALS')}")
    print(f"DEPOSITS: {header.find('DEPOSITS')}")
    print(f"BALANCE: {header.find('BALANCE')}")
    
    # Check Line 2 (Data)
    #   02-04-2025  TRF                                               100000.00      567115.55Dr
    line2 = lines[2]
    print(f"\nLine 2: {line2.rstrip()}")
    print(f"Index of '100000.00': {line2.find('100000.00')}")
    print(f"Index of '567115.55Dr': {line2.find('567115.55Dr')}")
    
    # Check Line 5 (Data with Withdrawal)
    #                POONAM DEV/PUNB001 509312716679         8000.00                  425115.55Dr
    line5 = lines[5]
    print(f"\nLine 5: {line5.rstrip()}")
    print(f"Index of '8000.00': {line5.find('8000.00')}")
    print(f"Index of '425115.55Dr': {line5.find('425115.55Dr')}")

    # Check Line 9 (Data with small withdrawal)
    #                POONAM DEV/PUNB001 509312716679            0.90                  425121.45Dr
    line9 = lines[9]
    print(f"\nLine 9: {line9.rstrip()}")
    print(f"Index of '0.90': {line9.find('0.90')}")

if __name__ == "__main__":
    check_indices(r"c:\Users\gurpr\.gemini\antigravity\AI PROJECTS\rpt converter\TMPDAAmL1n_dT12.RPT")
