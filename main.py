import os
import configparser

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from middleware import validate_ip
from photoshop_enhancer import process_folder, get_task_action
from schemas import EnhanceFolderRequestData, ProcessFolderResult

config = configparser.ConfigParser()
config.read('config.ini')

app = FastAPI()

app.middleware("http")(validate_ip)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []
    for error in errors:
        field = (error['loc'][1])
        message = error["msg"]
        pretty_message = ProcessFolderResult(status="validation_error",
                                             error=True,
                                             error_type=error["type"],
                                             error_message=f'''"{field}" {message}''')
        formatted_errors.append(pretty_message.json())
    return JSONResponse(
            status_code=422,
            content=formatted_errors,
        )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/enhance_folder/")
async def enhance_folder(data_dict: EnhanceFolderRequestData):
    root_folder = config['NETWORK_SETTINGS']['ROOT_FOLDER']
    folder_path = os.path.join(
        root_folder,
        data_dict.studio_name,
        data_dict.month,
        data_dict.day,
        data_dict.hour
    )

    print(f'data_dict: {data_dict}')

    if data_dict.task:
        folder_path += f"_task_{data_dict.cert_code}"

    action = data_dict.action_name
    try:
        result = await process_folder(
            folder=folder_path, studio_name=data_dict.studio_name,
            action=action, task=data_dict.task
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    print(f"process_folder result: {result}")

    if result.error:
        return JSONResponse(status_code=500, content=result.json())

    print(f"execution time: {result.execution_time:.2f} seconds")
    return result


@app.post("/test_enhance_action")
async def test_action(data_dict: EnhanceFolderRequestData):
    root_folder = "/cloud/reflect/files/"
    folder_path = os.path.join(
        root_folder,
        data_dict.studio_name,
        data_dict.month,
        data_dict.day,
        data_dict.hour
    )
    print(f'data_dict: {data_dict}')
    if data_dict.task:
        folder_path += f"_task_{data_dict.cert_code}"
    result = get_task_action(data_dict.studio_name, data_dict.action_name,
                             True, 'test_image_name_portrait')
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
