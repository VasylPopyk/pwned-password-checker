import os
import subprocess
import sys
from pathlib import Path

# ANSI color codes for terminal formatting / ANSI-коди кольорів для термінала
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"

def print_banner():
    # Display the main application banner / Виведення головного банера програми
    print(CYAN + "=" * 65)
    print("      SEC-AUDITOR INTERACTIVE CONSOLE (compiler.py)")
    print("      Security utility for password and breach checking")
    print("=" * 65 + RESET)

def show_directory_contents():
    """
    Displays the contents of the current working directory with color icons.
    Виводить вміст поточної робочої директорії з кольоровими іконками.
    """
    print(YELLOW + "\n[📁] Current directory contents:" + RESET)
    current_dir = Path(".")
    items = sorted(current_dir.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    
    for item in items:
        if item.name.startswith('.'):
            continue
        if item.is_dir():
            print(f"  {BLUE}📂 [DIR]{RESET}  {item.name}")
        else:
            print(f"  {GREEN}📄 [FILE]{RESET} {item.name}")
    print(CYAN + "-" * 65 + RESET)

def get_valid_mode():
    """
    Prompts the user to select a valid operating mode with error handling.
    Опитує користувача щодо вибору коректного режиму роботи з обробкою помилок.
    """
    while True:
        print(CYAN + "\nSelect utility operation mode:" + RESET)
        print(f"  {BOLD}[1]{RESET} passwords - Password check mode (hashing + complexity analysis + breaches)")
        print(f"  {BOLD}[2]{RESET} hashes    - Pre-computed SHA-1 hashes check mode for breaches")
        
        choice = input(YELLOW + "Enter 'passwords' or 'hashes' (or 1 / 2): " + RESET).strip().lower()
        
        if choice in ["1", "passwords", "p"]:
            return "passwords"
        elif choice in ["2", "hashes", "h"]:
            return "hashes"
        else:
            print(RED + "\n[-] ERROR: Invalid mode selection.")
            print("    Explanation: You need to enter the mode name or its number (1 or 2). Try again." + RESET)

def get_valid_file():
    """
    Prompts for a file path and verifies its existence.
    Запитує шлях до файлу та перевіряє його наявність.
    """
    while True:
        print(CYAN + "\n[Example input: passwords.txt, trash.txt or data.csv]" + RESET)
        filename = input(YELLOW + "Enter path to input file: " + RESET).strip()
        
        if not filename:
            print(RED + "\n[-] ERROR: File name cannot be empty." + RESET)
            continue
            
        if not Path(filename).exists():
            print(RED + f"\n[-] ERROR: File '{filename}' not found in the current directory.")
            print("    Explanation: Make sure the file exists and is located in the same folder." + RESET)
            
            show_help = input(YELLOW + "Would you like to view the list of available files? (y/n): " + RESET).strip().lower()
            if show_help == 'y':
                show_directory_contents()
            continue
            
        return filename

def main():
    print_banner()
    
    while True:
        print(CYAN + "\nMain Menu:" + RESET)
        print(f"  {BOLD}[1]{RESET} Run interactive setup wizard")
        print(f"  {BOLD}[2]{RESET} Show current directory contents (files/folders)")
        print(f"  {BOLD}[3]{RESET} Exit")
        
        action = input(YELLOW + "\nChoose an action (1-3): " + RESET).strip()
        
        if action == "2":
            show_directory_contents()
            continue
        elif action == "3":
            print(GREEN + "\nExiting the program. Goodbye!" + RESET)
            sys.exit(0)
        elif action == "1":
            break
        else:
            print(RED + "\n[-] ERROR: Please enter a number from 1 to 3." + RESET)

    # Step 1: Select mode / Крок 1: Вибір режиму
    mode = get_valid_mode()

    # Step 2: Input file / Крок 2: Вхідний файл
    input_file = get_valid_file()

    # Step 3: JSON report name / Крок 3: Назва JSON-звіту
    print(CYAN + "\n[Example input: report.json, audit_2026.json]" + RESET)
    json_output = input(YELLOW + "Enter name for output JSON report (Press Enter to print to console): " + RESET).strip()

    # Step 4: Additional hash file (passwords mode only) / Крок 4: Додатковий файл хешів (тільки для режиму passwords)
    hash_output = None
    if mode == "passwords":
        print(CYAN + "\n[Example input: hashes.txt, generated_sha1.txt]" + RESET)
        save_hashes = input(YELLOW + "Save generated SHA-1 hashes to a separate text file? (y/n): " + RESET).strip().lower()
        if save_hashes == 'y':
            hash_output = input(YELLOW + "Enter file name for hashes: " + RESET).strip()

    # Build command for the main script / Формування команди для головного скрипта
    cmd = [sys.executable, "script.py", "-f", input_file, "-m", mode]
    if json_output:
        cmd.extend(["-o", json_output])
    if hash_output:
        cmd.extend(["--hash-output", hash_output])

    # Demonstrate generated command / Демонстрація згенерованої команди
    print(CYAN + "\n" + "=" * 65)
    print("[+] GENERATED COMMAND FOR THE MAIN SCRIPT:")
    print("    " + " ".join(cmd))
    print("=" * 65 + RESET)

    confirm = input(YELLOW + "\nDo you want to run this command? (y/n): " + RESET).strip().lower()
    if confirm != 'y':
        print(RED + "\n[-] Execution cancelled by user." + RESET)
        return

    # Execute main script via subprocess / Запуск головного скрипта через subprocess
    print(CYAN + "\n[*] Running process... Please wait.\n" + "-" * 65 + RESET)
    try:
        subprocess.run(cmd, check=True)
        print(CYAN + "-" * 65 + RESET)
        print(GREEN + "[+] PROCESS SUCCESSFULLY COMPLETED!" + RESET)
        
        # Print intuitive mini-report / Виведення інтуїтивного міні-звіту
        print(CYAN + "\n" + "=" * 20 + " MINI-REPORT " + "=" * 20 + RESET)
        print(f" • Operation mode:    {BOLD}{mode}{RESET}")
        print(f" • Input file:        {BOLD}{input_file}{RESET}")
        if json_output:
            print(f" • JSON report:       {GREEN}{Path(json_output).resolve()}{RESET}")
        else:
            print(f" • JSON report:       {YELLOW}Printed to console{RESET}")
        if hash_output:
            print(f" • Hash file:         {GREEN}{Path(hash_output).resolve()}{RESET}")
        print(CYAN + "=" * 53 + RESET)

    except subprocess.CalledProcessError as e:
        print(RED + f"\n[-] ERROR: Main script returned error code: {e}" + RESET)

if __name__ == "__main__":
    main()