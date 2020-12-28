import logging

from telegram import Update, InlineQueryResultCachedGif
from telegram.ext import (
    CallbackContext,
    Filters,
    MessageHandler,
)

from ..common import filter_dict_none
from ..document import Document, DocumentType
from .common import ADDING_KEYWORDS_STATE, DOCUMENT_TO_INDEX_KEY
from .inline_search import inline_result_creator

logger = logging.getLogger(__name__)


def new_animation(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'User {user.id} sent an animation for indexing.')

    animation = update.message.document
    content = filter_dict_none({
        'file_id': animation.file_id,
        'file_unique_id': animation.file_unique_id,
        'file_name': animation.file_name,
        'mime_type': animation.mime_type,
        'file_size': animation.file_size,
        'caption': update.message.caption,
    })
    if animation.thumb:
        thumb = animation.thumb
        content['thumb'] = filter_dict_none({
            'file_id': thumb.file_id,
            'file_unique_id': thumb.file_unique_id,
            'width': thumb.width,
            'height': thumb.height,
            'file_size': thumb.file_size,
        })
    doc = Document(
        user_id=user.id,
        doc_type=DocumentType.ANIMATION,
        content=content,
    )
    context.chat_data[DOCUMENT_TO_INDEX_KEY] = doc

    update.effective_chat.send_message(text='Now send me keywords to index this animation.')
    return ADDING_KEYWORDS_STATE


@inline_result_creator(DocumentType.ANIMATION)
def create_animation_inline_result(id: str, doc: Document):
    content = doc.content
    return InlineQueryResultCachedGif(
        id=id,
        gif_file_id=content['file_id'],
        caption=content.get('caption'),
    )


new_animation_handler = MessageHandler(Filters.animation, new_animation)
