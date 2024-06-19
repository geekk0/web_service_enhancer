import os

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

    total_time = await process_folder(folder_path)

    print(f"Total execution time: {total_time:.2f} seconds")

    return {"message": f"Folder {folder_path} processed successfully"}
