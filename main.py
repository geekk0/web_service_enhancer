import os

from fastapi import FastAPI
from photoshop_enhancer import process_folder
from schemas import EnhanceFolderRequestData
from middleware import validate_ip


app = FastAPI()

app.middleware("http")(validate_ip)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/enhance_folder/")
async def enhance_folder(data_dict: EnhanceFolderRequestData):
    folder_path = os.path.join(r'Y:/test enhancement',
                               data_dict.studio_name,
                               data_dict.month,
                               data_dict.day,
                               data_dict.hour
                               )
    action = data_dict.action_name

    try:
        total_time, open_save_time, enhance_time = await process_folder(folder_path, action)
        print(f"Total execution time: {total_time:.2f} seconds")
        print(f"Open-save time: {open_save_time:.2f} seconds")
        print(f"Enhance time: {enhance_time:.2f} seconds")
        return {"message": f"Folder {folder_path} processed successfully"}

    except Exception as e:
        return {f"An error occurred: {e}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
