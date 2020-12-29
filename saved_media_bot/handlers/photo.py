import logging
from typing import Dict

from telegram import Message, InlineQueryResultCachedPhoto
from telegram.ext import Filters

from ..common import filter_dict_none
from ..document import Document, DocumentType

from .inline_search import inline_result_creator
from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.photo, DocumentType.PHOTO)
def photo_handler(message: Message) -> Dict:
    photos = message.photo
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
        'caption': message.caption,
    })
    return content


@inline_result_creator(DocumentType.PHOTO)
def photo_inline_result(id: str, doc: Document) -> InlineQueryResultCachedPhoto:
    content = doc.content
    return InlineQueryResultCachedPhoto(
        id=id,
        photo_file_id=content['best_photo'],
        title=doc.keywords,
        caption=content.get('caption'),
    )
