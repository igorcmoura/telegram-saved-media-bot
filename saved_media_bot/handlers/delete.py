import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    ChosenInlineResultHandler,
    Filters,
    MessageHandler,
)

from ..es_store import store

logger = logging.getLogger(__name__)

SELECTING_MEDIA_STATE = 0
DELETING_MEDIA_STATE = 1

CHAT_ON_DELETION_STATE_KEY = 'chat_on_deletion_state'


def begin_delete(update: Update, context: CallbackContext):
    """Step to store information about the chat where the deletion is happening"""

    user = update.message.from_user
    logger.info(f'User {user.name}({user.id}) stated a deletion.')

    update.effective_chat.send_message(
        text='Use the inline search to select the message for deletion.',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
            text='Select message',
            switch_inline_query_current_chat='',
        )]]),
    )

    context.bot_data[CHAT_ON_DELETION_STATE_KEY] = update.effective_chat.id
    return SELECTING_MEDIA_STATE


def check_selection(update: Update, context: CallbackContext):
    """Step to check if the user sent the message to the right chat and if they used the search query"""

    user = update.message.from_user
    chat = update.effective_chat
    logger.info(f'User {user.name}({user.id}) sent a message to delete on chat {chat.id}.')

    chat_on_deletion_state = context.bot_data.get(CHAT_ON_DELETION_STATE_KEY)
    if not chat_on_deletion_state:
        raise RuntimeError("Couldn't retrieve chat_id where deletion is happening.")

    if chat_on_deletion_state != chat.id:
        logger.info(f'User {user.name}({user.id}) sent the message to delete on the wrong chat.')
        return SELECTING_MEDIA_STATE

    message_bot = update.message.via_bot
    if not message_bot or message_bot.id != context.bot.id:
        logger.info(f"User {user.name}({user.id}) didn't use the search query to select message to delete.")
        update.effective_chat.send_message(
            text="Please use the inline search to select the message to delete.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                text='Select message',
                switch_inline_query_current_chat='',
            )]]),
        )
        return SELECTING_MEDIA_STATE

    return DELETING_MEDIA_STATE


def execute_deletion(update: Update, context: CallbackContext):
    """Step to delete the document from the database"""

    chat_id = context.bot_data.get(CHAT_ON_DELETION_STATE_KEY)
    if not chat_id:
        raise RuntimeError("Couldn't retrieve chat_id where deletion is happening.")

    logger.info(f"Deleting message on chat {chat_id}.")
    doc_id = update.chosen_inline_result.result_id
    store.delete(doc_id)

    context.bot.send_message(chat_id=chat_id, text="Message deleted.")
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'User {user.name}({user.id}) canceled the the delete.')
    update.effective_chat.send_message(text="Ok, canceling deletion.")

    return ConversationHandler.END


delete_handler = ConversationHandler(
    entry_points=[CommandHandler('delete', begin_delete)],
    states={
        SELECTING_MEDIA_STATE: [MessageHandler(Filters.all & (~Filters.command), check_selection)],
        DELETING_MEDIA_STATE: [ChosenInlineResultHandler(execute_deletion)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    per_chat=False,
)
