import logging

from telegram import Update, InlineQueryResultCachedPhoto
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


def new_photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'User {user.id} sent a photo for indexing.')

    photos = update.message.photo
    content = filter_dict_none({
        'photos': {
            photo.file_id: {
                'file_id': photo.file_id,
                'file_unique_id': photo.file_unique_id,
                'width': photo.width,
                'height': photo.height,
                'file_size': photo.file_size,
            }
            for photo in photos
        },
        'best_photo': max(photos, key=lambda p: p.file_size).file_id,
        'caption': update.message.caption,
    })

    doc = Document(
        user_id=user.id,
        doc_type=DocumentType.PHOTO,
        content=content,
    )
    context.chat_data[DOCUMENT_TO_INDEX_KEY] = doc

    update.effective_chat.send_message(text='Now send me keywords to index this photo.')
    return ADDING_KEYWORDS_STATE


@inline_result_creator(DocumentType.PHOTO)
def create_photo_inline_result(id: str, doc: Document):
    content = doc.content
    return InlineQueryResultCachedPhoto(
        id=id,
        photo_file_id=content['best_photo'],
        caption=content.get('caption'),
    )


new_photo_handler = MessageHandler(Filters.photo, new_photo)
