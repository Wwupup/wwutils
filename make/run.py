import os
import subprocess
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(script_dir)) 
build_dir = os.path.join(project_root, 'build')
def build():
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    try:
        subprocess.call(f"(cd {build_dir};cmake ..;make)", shell=True)
    except OSError:
        sys.exit("cmake error!")

def project_init():
    if not os.path.exists("CMakeLists.txt"):
        with open("CMakeLists.txt", 'w') as f:
            f.write('''
project(DEMO)
add_executable(main main.cpp)
            ''')

def run():
    print("="*20)
    subprocess.call(f"{os.path.join(build_dir, 'main')}", shell=True)
    print("="*20)
    
if __name__ == "__main__":
    project_init()
    build()
    run()