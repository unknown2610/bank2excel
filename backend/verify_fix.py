from rpt_parser import parse_rpt_file
import pandas as pd

# Create a dummy file with specific spacing if the artifact one isn't perfect, 
# but we will try to use the artifact one first.
# Indices based on code default/fallback:
# CHQ: 50
# WITH: 70
# DEP: 90
# BAL: 110

# Line construction to ensure numbers cross the boundary
# Header:
# 0........10........20........30........40........50........60........70........80........90.......100.......110.......120
#                                                   CHQ.NO.             WITHDRAWALS         DEPOSITS            BALANCE
# Data:
# "8000.00" (7 chars) placed to end at 75? No, start at 68.
# 68: '8', 69: '0', 70: '0'. 
# Old logic: CUT at 70. '80' goes to CHQ. '00.00' goes to WITH. -> Fail.
# New logic: CHQ end ~65? (len 7). 50+7=57. 
# WITH start 70. 
# Midpoint (57+70)//2 = 63.
# Slicing at 63.
# 68 is > 63. So '8000.00' goes to WITH. -> Pass.

# "425115.55Dr" (11 chars).
# BAL start 110.
# Place start at 108.
# Old logic: CUT at 110. '42' into DEP. -> Fail.
# New logic: DEP end 90+8=98. BAL start 110. Midpoint (98+110)//2 = 104.
# Slicing at 104.
# 108 > 104. So '42...' goes to BAL. -> Pass.

header = "DATE      PARTICULARS                             CHQ.NO.             WITHDRAWALS         DEPOSITS            BALANCE\n"
#         0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#                   10        20        30        40        50        60        70        80        90       100       110

row =    "03-04-2025 Test Margin Case                       509312716679      8000.00                                   425115.55Dr\n"
# Check indices:
# 8000.00 start verification:
start_8k = row.find("8000.00")
print(f"'8000.00' starts at index: {start_8k}") # Expect < 70

start_bal = row.find("425115.55Dr")
print(f"'425115.55Dr' starts at index: {start_bal}") # Expect < 110

with open("backend/test_gen.rpt", "w") as f:
    f.write(header)
    f.write(row)

print("Running parser...")
df = parse_rpt_file("backend/test_gen.rpt")
print(df)
print("\nExtracted Values:")
print(f"Withdrawals: '{df.iloc[0]['Withdrawals']}'")
print(f"Balance: '{df.iloc[0]['Balance']}'")

if df.iloc[0]['Withdrawals'] == 8000.0 and df.iloc[0]['Balance'] == 425115.55:
    print("SUCCESS: Values parsed correctly.")
else:
    print("FAILURE: Values mismatch.")
