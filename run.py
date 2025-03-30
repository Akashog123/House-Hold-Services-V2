import os
import sys
import subprocess
import webbrowser
import time
import venv

VENV_DIR = "venv"

def is_venv_created():
    return os.path.isdir(VENV_DIR) and os.path.isfile(os.path.join(VENV_DIR, "pyvenv.cfg"))

def get_venv_python():
    return os.path.join(VENV_DIR, "Scripts", "python.exe")

def create_venv():
    if not is_venv_created():
        print(f"Creating virtual environment in {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
        return True
    return False

def install_python_dependencies():
    python_exec = get_venv_python()
    if not os.path.exists(python_exec):
        print(f"ERROR: Virtual environment Python not found at {python_exec}")
        sys.exit(1)
    
    try:
        print("Installing Python dependencies...")
        subprocess.check_call([python_exec, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing Python dependencies: {e}")
        sys.exit(1)
def find_npm():
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Found npm version: {result.stdout.strip()}")
            return "npm"
    except FileNotFoundError:
        print("npm not found in PATH, searching common locations...")
    
    path = r"C:\Program Files\nodejs\npm.cmd"
    if os.path.isfile(path):
        return path
    
    print("\nERROR: npm not found. Please install Node.js:")
    sys.exit(1)

def install_npm_dependencies():
    if not os.path.isdir("node_modules"):
        print("Installing npm dependencies...")
        try:
            npm_path = find_npm()
            if npm_path:
                if npm_path == "npm":
                    subprocess.check_call(["npm", "install"])
                else:
                    subprocess.check_call([npm_path, "install"])
            else:
                print("ERROR: npm not found. Please ensure Node.js is installed.")
                sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error installing npm dependencies: {e}")
            sys.exit(1)
    else:
        print("npm dependencies already installed")

def start_backend():
    print("Starting Flask backend server...")
    python_exec = get_venv_python()
    
    if not os.path.exists(python_exec):
        print(f"ERROR: Virtual environment Python not found at {python_exec}")
        sys.exit(1)
    
    cmd = [python_exec, "-m", "flask", "run"]
    print(f"Running command: {' '.join(cmd)}")
    
    env = os.environ.copy()
    env["FLASK_APP"] = "backend.app"
    env["FLASK_ENV"] = "development"
    
    return subprocess.Popen(cmd, env=env, cwd=os.path.dirname(os.path.abspath(__file__)))

def start_frontend():
    print("Starting Vue frontend server with Vite...")
    npm_path = find_npm()
    
    if npm_path == "npm":
        cmd = ["npm", "run", "dev"]
    else:
        cmd = [npm_path, "run", "dev"]
    
    print(f"Running command: {' '.join(cmd)}")
    
    return subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

def main():
    print("Starting HouseCare application...")
    create_venv()
 
    try:
        install_python_dependencies()
        install_npm_dependencies()
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)
    
    # Start the backend server
    backend_process = start_backend()
    
    # Give the backend time to start
    time.sleep(2)
    
    # Start the frontend server
    frontend_process = start_frontend()
    
    # Give the frontend time to start
    time.sleep(5)
    
    # Open the browser to the frontend URL
    print("Opening browser to application...")
    webbrowser.open('http://localhost:5173')
    
    print("\nHouseCare Development Server")
    print("-------------------------")
    print("Frontend: http://localhost:5173")
    print("Backend API: http://localhost:5000/api")
    print("\nPress Ctrl+C to stop all servers")
    
    try:
        # Keep the script running to maintain the server processes
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        # Clean up processes when the user presses Ctrl+C
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers shut down successfully.")

if __name__ == "__main__":
    main()
