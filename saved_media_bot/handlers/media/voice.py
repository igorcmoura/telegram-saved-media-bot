import logging
from typing import Dict

from telegram import Message, InlineQueryResultCachedVoice
from telegram.ext import Filters

from ...common import filter_dict_none
from ...document import Document, DocumentType

from ..inline_search import inline_result_creator

from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.voice, DocumentType.VOICE)
def voice_handler(message: Message) -> Dict:
    voice = message.voice

    content = filter_dict_none({
        'file_id': voice.file_id,
        'file_unique_id': voice.file_unique_id,
        'duration': voice.duration,
        'mime_type': voice.mime_type,
        'file_size': voice.file_size,
    })
    return content


@inline_result_creator(DocumentType.VOICE)
def create_voice_inline_result(doc: Document) -> InlineQueryResultCachedVoice:
    content = doc.content
    return InlineQueryResultCachedVoice(
        id=doc.internal_id,
        voice_file_id=content['file_id'],
        title=doc.keywords,
        caption=content.get('caption'),
    )
