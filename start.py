import os
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

venv_path = os.path.join(script_dir, "webenv", "bin", "activate")
run_py_path = os.path.join(script_dir, "server", "run.py")

if not os.path.exists(venv_path):
    print(f"Error: Virtual environment not found at {venv_path}")
    sys.exit(1)

if not os.path.exists(run_py_path):
    print(f"Error: Run.py not found at {run_py_path}")
    sys.exit(1)

command = f"source {venv_path} && python {run_py_path}"

try:
    subprocess.run(command, shell=True, executable="/bin/bash", check=True)
except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)

