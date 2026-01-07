
def print_ruler_and_lines(file_path, num_lines=20):
    ruler1 = "0123456789" * 12
    ruler2 = ""
    for i in range(12):
        ruler2 += str(i) * 10
    
    print(f"    {ruler2}")
    print(f"    {ruler1}")
    
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= num_lines:
                break
            print(f"{i:2}: {line.rstrip()}")

if __name__ == "__main__":
    print_ruler_and_lines(r"c:\Users\gurpr\.gemini\antigravity\AI PROJECTS\rpt converter\TMPDAAmL1n_dT12.RPT")
