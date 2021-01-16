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

from ..document import Document
from ..es_store import store

logger = logging.getLogger(__name__)

SELECTING_MEDIA_STATE = 0
EDITING_MEDIA_STATE = 1
ADDING_KEYWORDS_STATE = 2

CHAT_ON_EDITING_STATE_KEY = 'chat_on_editing_state'
DOCUMENT_TO_EDIT_KEY = 'document_to_edit'


def begin_edit(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'User {user.name}({user.id}) started an editing.')

    update.effective_chat.send_message(
        text='Use the inline search to select the message to be edited.',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
            text='Select message',
            switch_inline_query_current_chat='',
        )]]),
    )

    context.bot_data[CHAT_ON_EDITING_STATE_KEY] = update.effective_chat.id
    return SELECTING_MEDIA_STATE


def check_selection(update: Update, context: CallbackContext):
    user = update.message.from_user
    chat = update.effective_chat
    logger.info(f'User {user.name}({user.id}) sent a message to be edited on chat {chat.id}.')

    chat_on_editing_state = context.bot_data.get(CHAT_ON_EDITING_STATE_KEY)
    if not chat_on_editing_state:
        raise RuntimeError("Couldn't retrieve chat_id where editing is happening.")

    if chat_on_editing_state != chat.id:
        logger.info(f'User {user.name}({user.id}) sent the message to be edited on the wrong chat.')
        return SELECTING_MEDIA_STATE

    message_bot = update.message.via_bot
    if not message_bot or message_bot.id != context.bot.id:
        logger.info(f"User {user.name}({user.id}) didn't use the search query to select message to be edited.")
        update.effective_chat.send_message(
            text="Please use the inline search to select the message to be edited.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                text='Select message',
                switch_inline_query_current_chat='',
            )]]),
        )
        return SELECTING_MEDIA_STATE

    return EDITING_MEDIA_STATE


def ask_for_keywords(update: Update, context: CallbackContext):
    chat_id = context.bot_data.get(CHAT_ON_EDITING_STATE_KEY)
    if not chat_id:
        raise RuntimeError("Couldn't retrieve chat_id where editing is happening.")

    logger.info(f"Editing message on chat {chat_id}.")
    doc_id = update.chosen_inline_result.result_id

    doc = store.get(doc_id)
    context.bot_data[DOCUMENT_TO_EDIT_KEY] = (doc_id, doc)

    context.bot.send_message(
        chat_id=chat_id,
        text='Send me the new keywords to this message. Currently they are:\n' +
        f'{doc.keywords}',
    )
    return ADDING_KEYWORDS_STATE


def edit_keywords(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'Editing document from user {user.name}({user.id}).')

    chat_on_editing_state = context.bot_data.get(CHAT_ON_EDITING_STATE_KEY)
    if not chat_on_editing_state:
        raise RuntimeError("Couldn't retrieve chat_id where editing is happening.")

    chat = update.effective_chat
    if chat_on_editing_state != chat.id:
        logger.info(f'User {user.name}({user.id}) sent the keywords to edit on the wrong chat.')
        return SELECTING_MEDIA_STATE

    doc_id: str
    doc: Document
    doc_id, doc = context.bot_data.get(DOCUMENT_TO_EDIT_KEY)
    if not doc_id or not doc:
        update.effective_chat.send_message(text="Something went wrong. Couldn't find document to edit.")
        return ConversationHandler.END

    doc.keywords = update.message.text
    store.update(doc_id, doc)
    update.effective_chat.send_message(text="The message keywords have been edited.")

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'User {user.name}({user.id}) canceled the the editing.')
    update.effective_chat.send_message(text="Ok, canceling editing.")

    return ConversationHandler.END


edit_handler = ConversationHandler(
    entry_points=[CommandHandler('edit', begin_edit)],
    states={
        SELECTING_MEDIA_STATE: [MessageHandler(Filters.all & (~Filters.command), check_selection)],
        EDITING_MEDIA_STATE: [ChosenInlineResultHandler(ask_for_keywords)],
        ADDING_KEYWORDS_STATE: [MessageHandler(Filters.text & (~Filters.command), edit_keywords)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    per_chat=False,
)
