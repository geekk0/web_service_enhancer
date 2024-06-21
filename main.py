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
    folder_path = os.path.join(r'Y:/test enhancement',  folder_path.replace('_', "/"))
    # folder_path = os.path.join(r'C:\Users\Gekk0\Pictures\Camera Roll', folder_path.replace('_', "/"))
    print(folder_path)

    if not os.path.isdir(folder_path):
        return {"message": f"Folder {folder_path} does not exist"}

    try:
        total_time, open_save_time, enhance_time = await process_folder(folder_path)
        print(f"Total execution time: {total_time:.2f} seconds")
        print(f"Open-save time: {open_save_time:.2f} seconds")
        print(f"Enhance time: {enhance_time:.2f} seconds")
        return {"message": f"Folder {folder_path} processed successfully"}
    except Exception as e:
        return {f"An error occurred: {e}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


