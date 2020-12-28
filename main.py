import logging
import os

from dotenv import load_dotenv
from telegram.ext import Updater

from saved_media_bot import handlers

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    updater = Updater(token=os.environ.get('TOKEN'))
    dispatcher = updater.dispatcher

    for handler in handlers:
        dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
