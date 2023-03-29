import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
workdir = os.path.abspath(os.path.dirname(__file__))

def get_token():
    with open(os.path.join(workdir, './token.txt'), 'r') as f:
        token = f.read()
    return token


if __name__ == '__main__':
    updater = Updater(token=get_token(), use_context=False, request_kwargs={'proxy_url': 'socks5://127.0.0.1:1080/'})
    updater.start_polling()
    updater.idle()