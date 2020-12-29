import logging
from typing import Dict

from telegram import Message, InlineQueryResultCachedVideo
from telegram.ext import Filters

from ..common import filter_dict_none
from ..document import Document, DocumentType

from .inline_search import inline_result_creator
from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.video, DocumentType.VIDEO)
def video_handler(message: Message) -> Dict:
    video = message.video

    content = filter_dict_none({
        'file_id': video.file_id,
        'file_unique_id': video.file_unique_id,
        'width': video.width,
        'height': video.height,
        'duration': video.duration,
        'file_name': video.file_name,
        'mime_type': video.mime_type,
        'file_size': video.file_size,
    })
    if video.thumb:
        thumb = video.thumb
        content['thumb'] = filter_dict_none({
            'file_id': thumb.file_id,
            'file_unique_id': thumb.file_unique_id,
            'width': thumb.width,
            'height': thumb.height,
            'file_size': thumb.file_size,
        })
    return content


@inline_result_creator(DocumentType.VIDEO)
def create_video_inline_result(id: str, doc: Document) -> InlineQueryResultCachedVideo:
    content = doc.content
    return InlineQueryResultCachedVideo(
        id=id,
        video_file_id=content['file_id'],
        title=doc.keywords,
        caption=content.get('caption'),
    )
