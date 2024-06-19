import os
import time
from photoshop import Session
from photoshop.api.enumerations import DialogModes
from photoshop.api import JPEGSaveOptions


async def process_folder(folder: str):
    action = identify_action(folder)

    if not action:
        return

    image_files = [f for f in os.listdir(folder) if f.endswith('.jpg')]
    start_time = time.time()

    try:
        with Session() as ps:
            ps.app.displayDialogs = DialogModes.DisplayNoDialogs

            for image_name in image_files:
                image_path = os.path.join(folder, image_name)
                doc = ps.app.open(image_path)
                ps.app.doAction(action, "Default Actions")
                options = JPEGSaveOptions(quality=5)
                doc.saveAs(image_path, options, asCopy=False)
                doc.close()

    except Exception as e:
        print(f"An error occurred: {e}")

    end_time = time.time()
    total_time = end_time - start_time
    return total_time


def identify_action(folder):
    studio_actions = {
        'Силуэт': 'silhouette_action',
        'Отражение': 'reflect_action',
        'Портрет': 'portrait_action',
        'KZ': 'kz_action'
    }

    for studio_action in studio_actions.keys():
        if studio_action in folder:
            return studio_actions[studio_action]
