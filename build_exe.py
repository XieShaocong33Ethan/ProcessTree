import os
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))

nuitka_command = [
    "python", "-m", "nuitka",
    "--standalone",
    '--onefile',
    '--windows-console-mode=disable',
    "--include-data-dir=%s=utils" % os.path.join(current_dir, "utils"),
    "--output-dir=%s" % os.path.join(current_dir, "dist"),
    "--output-filename=DecisionTreeManager.exe",
    "--enable-plugin=pyside6",
    "main.py" 
]

# 执行Nuitka编译命令
subprocess.run(nuitka_command, check=True)

print("Compilation completed. The executable file is located in the dist directory.")