import os
import subprocess

from fastapi import FastAPI
from photoshop_enhancer import process_folder

app = FastAPI()

commands_mapping = {
    "folders_qty": 'dir /ad /b | find /c /v ""',
}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/enhance_folder/{folder_path}")
async def enhance_folder(folder_path: str):
    # folder_path = os.path.join('mounted disk', folder_path)
    folder_path = os.path.join(r'C:\Users\Gekk0\Pictures\Camera Roll', folder_path.replace('_', "/"))
    print(folder_path)

    total_time = process_folder(folder_path)

    print(f"Total execution time: {total_time:.2f} seconds")

    return {"message": f"Folder {folder_path} processed successfully"}


@app.get("/run_cmd/{name}")
async def run_cmd(name: str):
    try:
        process = subprocess.Popen(commands_mapping[name], shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        process_stdout, process_stderr = process.communicate()

        print(f"process stdout: {process_stdout}")

        if process.returncode == 0:
            print(f"Command {name} executed successfully")
            return {"message": f"There are {process_stdout.replace('\n', '')} folders"}
        else:
            print(f"Error executing command {name}")
            return {"message": f"Error executing command {name}"}

    except Exception as e:
        print(f"Exception occurred: {e}")
        return {"message": f"Error executing command {name}: {e}"}