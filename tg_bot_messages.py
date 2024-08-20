import configparser

from aiogram import Bot, Dispatcher

config = configparser.ConfigParser()
config.read('config.ini')
token = config['NETWORK_SETTINGS']['BOT_TOKEN']
group_chat_id = config['NETWORK_SETTINGS']['REFLECT_GROUP_CHAT_ID']
bot = Bot(token)


def send_folder_enhanced_message(folder):
    bot.send_message(group_chat_id, f'Папка {folder} успешно обработана')