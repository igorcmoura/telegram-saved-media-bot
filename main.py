import logging

from telegram.ext import Updater

from saved_media_bot import Config, handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG if Config.DEBUG else logging.INFO
)


def main():
    updater = Updater(token=Config.TG_BOT_TOKEN)
    dispatcher = updater.dispatcher

    for handler in handlers:
        dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
