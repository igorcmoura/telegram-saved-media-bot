import logging
from typing import Dict

from telegram import Message, InlineQueryResultCachedGif
from telegram.ext import Filters

from ..common import filter_dict_none
from ..document import Document, DocumentType

from .inline_search import inline_result_creator
from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.animation, DocumentType.ANIMATION)
def animation_handler(message: Message) -> Dict:
    animation = message.document
    content = filter_dict_none({
        'file_id': animation.file_id,
        'file_unique_id': animation.file_unique_id,
        'file_name': animation.file_name,
        'mime_type': animation.mime_type,
        'file_size': animation.file_size,
        'caption': message.caption,
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
    return content


@inline_result_creator(DocumentType.ANIMATION)
def create_animation_inline_result(doc: Document) -> InlineQueryResultCachedGif:
    content = doc.content
    return InlineQueryResultCachedGif(
        id=doc.internal_id,
        gif_file_id=content['file_id'],
        title=doc.keywords,
        caption=content.get('caption'),
    )
