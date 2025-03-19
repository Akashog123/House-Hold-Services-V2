import os
import sys
import subprocess
import webbrowser
import time
import venv

# Define virtual environment path
VENV_DIR = "venv"

def is_venv_created():
    """Check if virtual environment exists"""
    return os.path.isdir(VENV_DIR) and os.path.isfile(os.path.join(VENV_DIR, "pyvenv.cfg"))

def get_venv_python():
    """Get the path to the Python executable in the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:  # Unix/Linux/MacOS
        return os.path.join(VENV_DIR, "bin", "python")

def create_venv():
    """Create a virtual environment if it doesn't exist"""
    if not is_venv_created():
        print(f"Creating virtual environment in {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
        return True
    return False

def install_python_dependencies():
    """Install Python dependencies in the virtual environment"""
    python_exec = get_venv_python()
    # Check if the venv python exists
    if not os.path.exists(python_exec):
        print(f"ERROR: Virtual environment Python not found at {python_exec}")
        sys.exit(1)
    
    # Uses the virtual env Python to install dependencies
    try:
        print("Installing Python dependencies...")
        subprocess.check_call([python_exec, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing Python dependencies: {e}")
        # Install Flask specifically since it's required
        print("Trying to install Flask directly...")
        subprocess.check_call([python_exec, "-m", "pip", "install", "flask", "flask-cors", "flask-jwt-extended"])

def find_npm():
    """Find npm executable even if it's not in PATH"""
    # Try directly (if it's in PATH)
    try:
        # Check if npm is responsive
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Found npm version: {result.stdout.strip()}")
            return "npm"
    except FileNotFoundError:
        print("npm not found in PATH, searching common locations...")
    
    # Common npm locations on Windows
    possible_paths = [
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
    ]
    
    # Check user's AppData location
    appdata = os.environ.get('APPDATA', '')
    if appdata:
        possible_paths.append(os.path.join(appdata, "npm"))
        possible_paths.append(os.path.join(os.path.dirname(appdata), "Local", "Programs", "nodejs", "npm.cmd"))
    
    # Add more common Node.js installation paths
    program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
    
    possible_paths.extend([
        os.path.join(program_files, "nodejs", "npm.cmd"),
        os.path.join(program_files_x86, "nodejs", "npm.cmd"),
    ])
    
    for path in possible_paths:
        if os.path.isfile(path):
            print(f"Found npm at: {path}")
            return path
    
    # If npm is not found, provide instructions for installation
    print("\nERROR: npm not found. Please install Node.js:")
    print("1. Download Node.js from https://nodejs.org/")
    print("2. Run the installer and follow the instructions")
    print("3. After installation, restart this script\n")
    sys.exit(1)

def install_npm_dependencies():
    """Install npm dependencies if needed"""
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
    """Start the Flask backend server using the virtual environment's Python"""
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
    """Start the Vue frontend server with npm"""
    print("Starting Vue frontend server with Vite...")
    npm_path = find_npm()
    
    if npm_path == "npm":
        cmd = ["npm", "run", "dev"]
    else:
        cmd = [npm_path, "run", "dev"]
    
    print(f"Running command: {' '.join(cmd)}")
    
    return subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function to start both servers"""
    print("Starting HouseCare application...")
    
    # Setup virtual environment
    create_venv()
    
    # Install dependencies
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
