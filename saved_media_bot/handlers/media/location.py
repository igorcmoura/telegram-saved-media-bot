import logging
from typing import Dict

from telegram import Message, InlineQueryResultLocation
from telegram.ext import Filters

from ...common import filter_dict_none
from ...document import Document, DocumentType

from ..inline_search import inline_result_creator

from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.location, DocumentType.LOCATION)
def location_handler(message: Message) -> Dict:
    location = message.location
    content = filter_dict_none({
        'longitude': location.longitude,
        'latitude': location.latitude,
        'horizontal_accuracy': location.horizontal_accuracy,
    })
    return content


@inline_result_creator(DocumentType.LOCATION)
def location_inline_result(doc: Document) -> InlineQueryResultLocation:
    content = doc.content
    return InlineQueryResultLocation(
        id=doc.internal_id,
        latitude=content['latitude'],
        longitude=content['longitude'],
        title=doc.keywords,
        horizontal_accuracy=content.get('horizontal_accuracy'),
    )
