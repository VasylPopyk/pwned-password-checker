import argparse
import csv
import hashlib
import json
import sys
import requests

def analyze_complexity(password):
    """Analysis of password complexity according to corporate standards."""
    """Аналізує складність пароля згідно з корпоративними стандартами."""
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    score = 0
    feedback = []
    
    if length >= 12:
        score += 2
    elif length >= 8:
        score += 1
        feedback.append("Extend the password length to at least 12 characters.")
    else:
        feedback.append("Password is too short (less than 8 characters).")
        
    if has_upper: score += 1
    else: feedback.append("Add uppercase letters.")
        
    if has_lower: score += 1
    else: feedback.append("Add lowercase letters.")
        
    if has_digit: score += 1
    else: feedback.append("Add digits.")
        
    if has_special: score += 1
    else: feedback.append("Add special characters.")    
    if score >= 5: level = "High"
    elif score >= 3: level = "Medium"
    else: level = "Low"
        
    return {
        "length": length,
        "complexity_level": level,
        "is_corporate_compliant": score >= 4,
        "feedback": feedback
    }

def check_hibp(sha1_hash):
    """Secure check through HIBP API with k-anonymity."""
    sha1_hash = sha1_hash.upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]
    
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        response = requests.get(url, headers={"User-Agent": "Corporate-Password-Validator"}, timeout=10)
        if response.status_code != 200:
            return {"compromised": False, "count": 0, "error": f"API status {response.status_code}"}
            
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                return {"compromised": True, "count": int(count), "error": None}
        return {"compromised": False, "count": 0, "error": None}
    except requests.RequestException as e:
        return {"compromised": False, "count": 0, "error": str(e)}

def read_input_file(filepath):
    items = []
    try:
        if filepath.endswith('.csv'):
            with open(filepath, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row: items.append(row[0].strip())
        else:
            with open(filepath, mode='r', encoding='utf-8') as f:
                for line in f:
                    val = line.strip()
                    if val: items.append(val)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    return items

def main():
    parser = argparse.ArgumentParser(description="Automated password validator and breach check.")
    parser.add_argument("-f", "--file", required=True, help="Path to the input file (.txt or .csv)")
    parser.add_argument("-m", "--mode", required=True, choices=["passwords", "hashes"], help="Operation mode")
    parser.add_argument("-o", "--output", help="Path to the output JSON file for the report")
    parser.add_argument("--hash-output", help="Path to the file for saving generated SHA-1 hashes (only for passwords mode)")

    args = parser.parse_args()
    data = read_input_file(args.file)
    
    report_data = {
        "mode": args.mode,
        "total_checked": len(data),
        "results": []
    }

    generated_sha1_hashes = []

    if args.mode == "passwords":
        for pwd in data:
            sha1_hash = hashlib.sha1(pwd.encode('utf-8')).hexdigest()
            sha256_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
            
            # Saving SHA-1 for a separate file
            generated_sha1_hashes.append(sha1_hash)
            
            complexity = analyze_complexity(pwd)
            hibp_res = check_hibp(sha1_hash)
            
            item_result = {
                "input_type": "password",
                "hashes": {"sha1": sha1_hash, "sha256": sha256_hash},
                "complexity": complexity,
                "breach_status": hibp_res
            }
            report_data["results"].append(item_result)

    elif args.mode == "hashes":
        for hval in data:
            hibp_res = check_hibp(hval)
            item_result = {
                "input_type": "hash",
                "hash_value": hval,
                "breach_status": hibp_res
            }
            report_data["results"].append(item_result)

    # Saving JSON report
    json_output = json.dumps(report_data, ensure_ascii=False, indent=4)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"Report successfully saved to file: {args.output}")
    else:
        print(json_output)

    # Additional saving of hashes to a text file, if the parameter is specified
    if args.hash_output and generated_sha1_hashes:
        with open(args.hash_output, 'w', encoding='utf-8') as f:
            f.write("\n".join(generated_sha1_hashes) + "\n")
        print(f"SHA-1 hashes successfully saved to file: {args.hash_output}")

if __name__ == "__main__":
    main()