import logging

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from .delete import delete_handler
from .edit import edit_handler
from .new_entry import new_entry_handler
from .inline_search import inline_search_handler

logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'User {user.name}({user.id}) started a conversation.')
    context.bot.send_message(chat_id=update.effective_chat.id, text="Send me a file and I'll save it for you.")


start_handler = CommandHandler('start', start_command)

handlers = [
    start_handler,
    delete_handler,
    edit_handler,
    new_entry_handler,
    inline_search_handler,
]
