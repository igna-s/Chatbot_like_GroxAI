import os
import subprocess
import sys

# --- Configuration ---
REPO_URL = "https://github.com/IAHispano/Applio"
REPO_DIR = "Applio"
APP_FILE = "app.py"

def run_command(command):
    """Executes a command in the terminal and handles errors."""
    try:
        # We use shell=True for simple commands like those in this script.
        # We use sys.executable to ensure the same Python interpreter is used.
        process = subprocess.run(command, shell=True, check=True, text=True)
        return process.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e}")
        return False

def main():
    """Main function of the script."""
    # 1. Clone the repository if it doesn't exist
    if not os.path.exists(REPO_DIR):
        print(f"[INFO] Cloning repository from {REPO_URL}...")
        if not run_command(f"git clone {REPO_URL}"):
            print("Error: Failed to clone the repository. Do you have Git installed?")
            return
    else:
        print("[INFO] 'Applio' directory already exists, skipping clone.")

    # Change to the repository directory
    try:
        os.chdir(REPO_DIR)
    except FileNotFoundError:
        print(f"Error: Directory '{REPO_DIR}' not found.")
        return

    print(f"[INFO] Current working directory: {os.getcwd()}")

    # 2. Install dependencies
    print("[INFO] Installing dependencies from requirements.txt...")
    # We use sys.executable to ensure we use pip of the correct Python version
    if not run_command(f'"{sys.executable}" -m pip install -r requirements.txt'):
        print("Error: Could not install dependencies.")
        return

    # 3. Run the application
    print(f"[INFO] Starting the application ({APP_FILE})...")
    if not run_command(f'"{sys.executable}" {APP_FILE}'):
        print("Error: Failed to launch the application.")
        return

if __name__ == "__main__":
    main()
    input("Press Enter to exit.")