import logging
from typing import Dict

from telegram import Message, InlineQueryResultCachedDocument
from telegram.ext import Filters

from ..common import filter_dict_none
from ..document import Document, DocumentType

from .inline_search import inline_result_creator
from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.document, DocumentType.DOCUMENT)
def document_handler(message: Message) -> Dict:
    document = message.document

    content = filter_dict_none({
        'file_id': document.file_id,
        'file_unique_id': document.file_unique_id,
        'file_name': document.file_name,
        'mime_type': document.mime_type,
        'file_size': document.file_size,
        'caption': message.caption
    })
    if document.thumb:
        thumb = document.thumb
        content['thumb'] = filter_dict_none({
            'file_id': thumb.file_id,
            'file_unique_id': thumb.file_unique_id,
            'width': thumb.width,
            'height': thumb.height,
            'file_size': thumb.file_size,
        })
    return content


@inline_result_creator(DocumentType.DOCUMENT)
def create_document_inline_result(id: str, doc: Document) -> InlineQueryResultCachedDocument:
    content = doc.content
    return InlineQueryResultCachedDocument(
        id=id,
        document_file_id=content['file_id'],
        title=doc.keywords,
        description=content['file_name'],
        caption=content.get('caption'),
    )
