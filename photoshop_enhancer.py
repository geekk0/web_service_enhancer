import configparser
import os
import time
import logging

from photoshop import Session
from photoshop.api.enumerations import DialogModes
from photoshop.api import JPEGSaveOptions
from PIL import Image

from schemas import ProcessFolderResult
from tg_bot_messages import send_folder_enhanced_message

config = configparser.ConfigParser()
config.read('config.ini')

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "process_folder.log"),
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)
logging.getLogger("comtypes").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def process_folder(
        folder: str,
        studio_name: str,
        action: str,
        attempt_counter: int = 1,
        task: bool = False
) -> ProcessFolderResult:


    start_time = time.time()

    logger.info(f'folder: {folder}')
    logger.info(f'studio_name: {studio_name}')
    logger.info(f'action: {action}')
    logger.info(f"[DEBUG] action = {action!r}, type = {type(action)}")
    logger.info(f'attempt_counter: {attempt_counter}')
    logger.info(f'task: {task}')

    enhance_error = False

    shared_folder = config['NETWORK_SETTINGS']['ROOT_FOLDER']
    if not check_shared_folder(shared_folder):
        return ProcessFolderResult(status="failed",
                                   error=True,
                                   error_type="FileNotFoundError",
                                   error_message=f"Shared folder {shared_folder} is unavailable")

    logger.info(f'folder: {folder}')

    try:
        image_files = [f for f in os.listdir(folder) if f.lower().endswith('.jpg')]
    except FileNotFoundError:
        logger.error(f"Folder {folder} not found")
        return ProcessFolderResult(status="failed",
                                   error=True,
                                   error_type="FileNotFoundError",
                                   error_message=f"Folder {folder} not found")

    destination_path = f'{folder}_BW' if "bw" in action else f'{folder}_AI'
    logger.info(f'destination_path: {destination_path}')

    if not os.path.exists(destination_path):
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

            logger.info(f'Processing folder: {destination_path}')
            print(f'Processing folder: {destination_path}')
            print(f"attempt_counter: {attempt_counter}")

            for image_name in image_files:
                if not os.path.isfile(os.path.join(destination_path, image_name)):
                    doc = None
                    try:
                        if "Neo_portrait" in image_name:
                            selected_action = "Neo_portrait_1"
                        else:
                            selected_action = action
                        logger.info(f"Processing image: {image_name}")
                        print(f"Processing image: {image_name}")
                        image_path = os.path.join(folder, image_name)
                        source_image_path = os.path.join(folder, image_name)
                        destination_image_path = os.path.join(destination_path, image_name)

                        photo_is_bw = is_black_white(source_image_path)

                        if photo_is_bw and "bw" not in action:
                            selected_action = f'{action}_bw'

                        if 'Neo2' in image_path:
                            if 'portrait' in image_name:
                                selected_action = 'Neo2_portrait'
                            else:
                                selected_action = 'Neo2'
                            if is_black_white(source_image_path):
                                selected_action = f'{selected_action}_bw'

                        doc = ps.app.open(image_path)
                        options = JPEGSaveOptions(quality=12)
                        if task:
                            action_for_photo = get_task_action(
                                studio_name, action,
                                photo_is_bw, image_name
                            )
                            logger.info(f"action_for_photo: {action_for_photo}")
                            print(f"action_for_photo: {action_for_photo}")
                            enhance_photo_error = False
                            try:
                                logger.info(f"Active document: {ps.app.activeDocument.name}")
                                active_layer = doc.activeLayer
                                logger.info(f"Active layer for '{image_name}': {active_layer.name}")
                            except Exception as e:
                                logger.warning(f"Can't get active layer for '{image_name}': {e}")
                            try:
                                ps.app.doAction(action_for_photo, "Retouch v2.0")
                            except Exception as e:
                                logger.error(f"doing action '{action_for_photo}' error: {e}")
                                print(f"doing action '{action_for_photo}' error: {e}")
                                enhance_photo_error = True
                            # if not enhance_photo_error:
                            #     action_for_photo = "Topaz"
                            #     try:
                            #         ps.app.doAction(action_for_photo, "Retouch v2.0")
                            #     except Exception as e:
                            #         logger.error(f"doing action 'Topaz' error: {e}")
                            #         print(f"doing action 'Topaz' error: {e}")
                            #         enhance_photo_error = True
                        else:
                            logger.info(f"action: {selected_action}")
                            ps.app.doAction(selected_action, "reflect_studio")

                        try:
                            doc.saveAs(destination_image_path, options, asCopy=False)
                        except Exception as e:
                            logger.error(f"save error: {e}")
                            enhance_error = True
                    except Exception as e:
                        logger.error(f"global enhance_error: {e}")
                        enhance_error = True

                    finally:
                        if doc is not None:
                            try:
                                doc.close()
                            except Exception as e:
                                logger.warning(f"Error closing document for '{image_name}': {e}")

                    time.sleep(0.5)

    except Exception as e:
        logger.info(e)
        return ProcessFolderResult(status='failed',
                                   error=True,
                                   error_message=str(e))


    # if not enhance_error:
    #     result = ProcessFolderResult(message="Folder processed successfully",
    #                                  status="success",
    #                                  error=False,
    #                                  execution_time=execution_time)
    #     notify_folder_processed(folder)
    # else:
    #     result = ProcessFolderResult(message="Error occurred while processing folder",
    #                                  status="failed",
    #                                  error=True)
    if enhance_error:
        if attempt_counter < 3:
            attempt_counter += 1
            return await process_folder(folder, studio_name, action, attempt_counter, task)
        else:
            result = ProcessFolderResult(status="failed",
                                         error=True,
                                         error_type="enhance_error",
                                         error_message="Error occurred while processing folder")
    else:
        folder_is_full = check_full_folder(destination_path)
        if folder_is_full:
            notify_folder_processed(folder)
            end_time = time.time()
            execution_time = end_time - start_time
            result = ProcessFolderResult(
                message="Folder processed successfully",
                status="success",
                error=False,
                execution_time=execution_time,
                folder_name=os.path.basename(destination_path)
            )
        else:
            result = ProcessFolderResult(status="failed",
                                         error=True,
                                         error_type="enhance_error",
                                         error_message="folder is not full")

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


def check_full_folder(folder_path):
    num_source_files = len([f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))])
    num_enhanced_files = len([f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))])
    if num_enhanced_files >= num_source_files:
        return True


def notify_folder_processed(folder_path):
    send_folder_enhanced_message(folder_path)


def get_task_action(
    studio_name, initial_action, photo_is_bw, image_name
) -> str | None:
    studios = {
        'Neo': 'Neo',
        'Neo2': 'Neo2',
        'Портрет(ЗАЛ)': 'portrait',
        'Силуэт': 'reflex',
        'Отражение': 'reflex'
    }
    try:
        current_action = studios[studio_name]
        logger.info(f"image name: {image_name}")
        if all(x in image_name for x in ('Neo', 'portrait')):
            current_action += "_portrait"
            logger.info('added _portrait')
        current_action += f"_{initial_action}"
        if photo_is_bw:
            retouch_setting = initial_action.split('_')[0]
            current_action = f'{current_action.replace(
                f"_{initial_action}", '')}_{retouch_setting}_bw'
        return current_action

    except Exception as e:
        logger.info(e)
        return None


def action_exists_in_set(action_name: str, set_name: str) -> bool:
    with Session() as ps:
        # Получаем список наборов
        action_sets = ps.app.actionSets
        for i in range(1, action_sets.count + 1):
            if action_sets[i].name == set_name:
                actions = action_sets[i].actions
                for j in range(1, actions.count + 1):
                    if actions[j].name == action_name:
                        return True
        return False




