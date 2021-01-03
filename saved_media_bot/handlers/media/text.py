import logging
from typing import Dict

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
    MessageEntity,
)
from telegram.ext import Filters

from ...common import filter_dict_none
from ...document import Document, DocumentType

from ..inline_search import inline_result_creator

from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.text & (~Filters.command), DocumentType.TEXT)
def text_handler(message: Message) -> Dict:
    content = filter_dict_none({
        'text': message.text,
        'entities': [
            filter_dict_none({
                'type': entity.type,
                'offset': entity.offset,
                'length': entity.length,
                'url': entity.url,
                'language': entity.language,
                # TODO: add support to user field
            })
            for entity in message.entities
        ],
    })
    return content


@inline_result_creator(DocumentType.TEXT)
def text_inline_result(doc: Document) -> InlineQueryResultArticle:
    content = doc.content
    return InlineQueryResultArticle(
        id=doc.internal_id,
        title=doc.keywords,
        input_message_content=InputTextMessageContent(
            message_text=content['text'],
            entities=[
                MessageEntity(
                    type=entity['type'],
                    offset=entity['offset'],
                    length=entity['length'],
                    url=entity.get('url'),
                    language=entity.get('language'),
                    # TODO: add support to user field
                )
                for entity in content['entities']
            ],
        )
    )
