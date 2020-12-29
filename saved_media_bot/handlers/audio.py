import logging
from typing import Dict

from telegram import Message, InlineQueryResultCachedAudio
from telegram.ext import Filters

from ..common import filter_dict_none
from ..document import Document, DocumentType

from .inline_search import inline_result_creator
from .media_handler import media_handler, MediaHandlingError

logger = logging.getLogger(__name__)


@media_handler(Filters.audio, DocumentType.AUDIO)
def audio_handler(message: Message) -> Dict:
    audio = message.audio
    if not audio.title:
        raise MediaHandlingError('Invalid audio file, it must have a title metadata.')

    content = filter_dict_none({
        'file_id': audio.file_id,
        'file_unique_id': audio.file_unique_id,
        'duration': audio.duration,
        'performer': audio.performer,
        'title': audio.title,
        'file_name': audio.file_name,
        'mime_type': audio.mime_type,
        'file_size': audio.file_size,
    })
    if audio.thumb:
        thumb = audio.thumb
        content['thumb'] = filter_dict_none({
            'file_id': thumb.file_id,
            'file_unique_id': thumb.file_unique_id,
            'width': thumb.width,
            'height': thumb.height,
            'file_size': thumb.file_size,
        })
    return content


@inline_result_creator(DocumentType.AUDIO)
def create_audio_inline_result(id: str, doc: Document) -> InlineQueryResultCachedAudio:
    content = doc.content
    return InlineQueryResultCachedAudio(
        id=id,
        audio_file_id=content['file_id'],
        caption=content.get('caption'),
    )
