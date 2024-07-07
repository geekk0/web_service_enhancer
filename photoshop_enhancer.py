import configparser
import os
import time

from photoshop import Session
from photoshop.api.enumerations import DialogModes
from photoshop.api import JPEGSaveOptions
from PIL import Image

from schemas import ProcessFolderResult

config = configparser.ConfigParser()
config.read('config.ini')


async def process_folder(folder: str, action: str) -> ProcessFolderResult:

    start_time = time.time()

    shared_folder = config['NETWORK_SETTINGS']['ROOT_FOLDER']
    if not check_shared_folder(shared_folder):
        return ProcessFolderResult(status="failed",
                                   error=True,
                                   error_type="FileNotFoundError",
                                   error_message=f"Shared folder {shared_folder} is unavailable")

    try:
        image_files = [f for f in os.listdir(folder) if f.lower().endswith('.jpg')]
    except FileNotFoundError:
        return ProcessFolderResult(status="failed",
                                   error=True,
                                   error_type="FileNotFoundError",
                                   error_message=f"Folder {folder} not found")

    destination_path = f'{folder}_RS'

    try:
        os.mkdir(destination_path)
    except FileExistsError:
        return ProcessFolderResult(status="failed",
                                   error=True,
                                   error_type="FileExistsError",
                                   error_message=f"Folder {destination_path} already exists")

    try:
        with Session() as ps:
            ps.app.displayDialogs = DialogModes.DisplayNoDialogs

            for image_name in image_files:
                selected_action = action
                print(f"Processing image: {image_name}")
                image_path = os.path.join(folder, image_name)
                source_image_path = os.path.join(folder, image_name)
                destination_image_path = os.path.join(destination_path, image_name)

                if is_black_white(source_image_path):
                    selected_action = f'{action}_bw'

                print(selected_action)

                doc = ps.app.open(image_path)
                ps.app.doAction(selected_action, "reflect_studio")
                options = JPEGSaveOptions(quality=12)
                doc.saveAs(destination_image_path, options, asCopy=False)
                doc.close()


    except Exception as e:
        return ProcessFolderResult(error=True, error_message=e)

    end_time = time.time()
    execution_time = end_time - start_time
    result = ProcessFolderResult(message="Folder processed successfully",
                                 status="success",
                                 execution_time=execution_time)
    return result


def is_black_white(image_path):

    with open(image_path, 'rb') as f:
        image = Image.open(f)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        colors = set(image.getdata())

        return True if len(colors) < 600 else False


def check_shared_folder(shared_folder):
    if os.path.exists(shared_folder):
        return True