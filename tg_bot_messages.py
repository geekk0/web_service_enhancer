import configparser
import telebot

config = configparser.ConfigParser()
config.read('config.ini')
token = config['NETWORK_SETTINGS']['BOT_TOKEN']
group_chat_id = config['NETWORK_SETTINGS']['REFLECT_GROUP_CHAT_ID']

bot = telebot.TeleBot(token)


def send_folder_enhanced_message(folder):
    bot.send_message(group_chat_id, f'Папка {folder} успешно обработана')


# def send_folder_enhanced_message(group_chat_id, folder):
#     asyncio.run(send_message(group_chat_id, f'Папка {folder} успешно обработана'))
#
#
# async def send_message(chat_id, message):
#     await bot.send_message(chat_id, message)
#
# send_folder_enhanced_message(group_chat_id, 'folder_path')




