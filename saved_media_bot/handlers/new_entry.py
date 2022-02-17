import logging

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from ..document import Document
from ..es_store import store

from .media import (
    ADDING_KEYWORDS_STATE, DOCUMENT_TO_INDEX_KEY,
    audio_handler,
    animation_handler,
    contact_handler,
    document_handler,
    location_handler,
    photo_handler,
    sticker_handler,
    text_handler,
    video_handler,
    voice_handler,
)

logger = logging.getLogger(__name__)


def add_keywords(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'Indexing new document from user {user.name}({user.id}).')

    doc: Document = context.chat_data.get(DOCUMENT_TO_INDEX_KEY)
    if not doc:
        update.effective_chat.send_message(text="Something went wrong. Couldn't find document to index.")
        return ConversationHandler.END

    doc.keywords = update.message.text
    store.save(doc)
    update.effective_chat.send_message(text="You can now search it using inline search.")

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'User {user.name}({user.id}) canceled the the new document indexing.')
    update.effective_chat.send_message(text="Ok, I won't index this message.")

    return ConversationHandler.END


new_entry_handler = ConversationHandler(
    entry_points=[
        audio_handler,
        animation_handler,
        contact_handler,
        document_handler,
        location_handler,
        photo_handler,
        sticker_handler,
        video_handler,
        voice_handler,
        # Some of the other handlers also accept text, so text_handler should be last to handle only pure text messages
        text_handler,
    ],
    states={
        ADDING_KEYWORDS_STATE: [MessageHandler(Filters.text & (~Filters.command), add_keywords)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
