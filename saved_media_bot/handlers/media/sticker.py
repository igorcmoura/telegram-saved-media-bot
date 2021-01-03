import logging
from typing import Dict

from telegram import Message, InlineQueryResultCachedSticker
from telegram.ext import Filters

from ...common import filter_dict_none
from ...document import Document, DocumentType

from ..inline_search import inline_result_creator

from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.sticker, DocumentType.STICKER)
def sticker_handler(message: Message) -> Dict:
    sticker = message.sticker
    content = filter_dict_none({
        'file_id': sticker.file_id,
        'file_unique_id': sticker.file_unique_id,
        'width': sticker.width,
        'height': sticker.height,
        'is_animated': sticker.is_animated,
        'emoji': sticker.emoji,
        'set_name': sticker.set_name,
        'file_size': sticker.file_size,
    })
    if sticker.thumb:
        thumb = sticker.thumb
        content['thumb'] = filter_dict_none({
            'file_id': thumb.file_id,
            'file_unique_id': thumb.file_unique_id,
            'width': thumb.width,
            'height': thumb.height,
            'file_size': thumb.file_size,
        })
    if sticker.mask_position:
        mask_position = sticker.mask_position
        content['mask_position'] = filter_dict_none({
            'point': mask_position.point,
            'x_shift': mask_position.x_shift,
            'y_shift': mask_position.y_shift,
            'scale': mask_position.scale,
        })
    return content


@inline_result_creator(DocumentType.STICKER)
def sticker_inline_result(doc: Document) -> InlineQueryResultCachedSticker:
    content = doc.content
    return InlineQueryResultCachedSticker(
        id=doc.internal_id,
        sticker_file_id=content['file_id'],
    )
