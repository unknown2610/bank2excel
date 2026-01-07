import pdfplumber

def analyze_columns(pdf_path):
    print(f"Analyzing {pdf_path}...")
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()
        
        # Find header words
        headers = ["Date", "Particulars", "Withdrawals", "Deposits", "Balance"]
        header_positions = {}
        
        for word in words:
            if word['text'] in headers:
                header_positions[word['text']] = word
                print(f"Found {word['text']}: x0={word['x0']}, x1={word['x1']}, top={word['top']}")

        # Attempt to guess dividing lines
        # Line 1: After Date (approx 50-70?)
        # Line 2: After Particulars (depends on page width, usually huge)
        # Line 3: After Withdrawals
        # Line 4: After Deposits
        
        # We can also look at the graphical lines if they exist
        lines = page.lines
        print(f"\nFound {len(lines)} distinct lines on page 1.")
        # Filter vertical lines
        v_lines = [l for l in lines if l['height'] > 5 and l['width'] < 5]
        print(f"Vertical lines x-coords: {[l['x0'] for l in v_lines]}")

if __name__ == "__main__":
    analyze_columns("AccountStmt_1761195605574.pdf")
