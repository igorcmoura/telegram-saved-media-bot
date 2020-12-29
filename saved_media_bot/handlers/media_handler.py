from functools import wraps
import logging
from typing import Callable

from telegram import Message, Update
from telegram.ext import (
    BaseFilter,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
)

from ..document import Document, DocumentType

logger = logging.getLogger(__name__)

ADDING_KEYWORDS_STATE = 0
DOCUMENT_TO_INDEX_KEY = 'document_to_index'


class MediaHandlingError(Exception):
    def __init__(self, msg: str, *args: object):
        super().__init__(*args)
        self.msg = msg


def media_handler(filters: BaseFilter, doc_type: DocumentType):
    """Decorator for functions that extract media content from messages."""
    def decorator(create_content: Callable[[Message], Document]):
        @wraps(create_content)
        def handler_callback(update: Update, context: CallbackContext):
            user = update.message.from_user
            logger.info(f'User {user.name}({user.id}) sent a message({doc_type.value}) for indexing.')

            try:
                content = create_content(update.message)
            except MediaHandlingError as e:
                update.effective_chat.send_message(text=e.msg)
                return ConversationHandler.END

            doc = Document(
                user_id=user.id,
                doc_type=doc_type,
                content=content,
            )
            context.chat_data[DOCUMENT_TO_INDEX_KEY] = doc

            update.effective_chat.send_message(text='Now send me keywords to index this message.')
            return ADDING_KEYWORDS_STATE
        return MessageHandler(filters, handler_callback)
    return decorator
