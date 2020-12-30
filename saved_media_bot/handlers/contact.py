import logging
from typing import Dict

from telegram import Message, InlineQueryResultContact
from telegram.ext import Filters

from ..common import filter_dict_none
from ..document import Document, DocumentType

from .inline_search import inline_result_creator
from .media_handler import media_handler

logger = logging.getLogger(__name__)


@media_handler(Filters.contact, DocumentType.CONTACT)
def contact_handler(message: Message) -> Dict:
    contact = message.contact

    content = filter_dict_none({
        'phone_number': contact.phone_number,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'user_id': contact.user_id,
        'vcard': contact.vcard,
    })
    return content


@inline_result_creator(DocumentType.CONTACT)
def create_contact_inline_result(doc: Document) -> InlineQueryResultContact:
    content = doc.content
    return InlineQueryResultContact(
        id=doc.internal_id,
        phone_number=content['phone_number'],
        first_name=content['first_name'],
        last_name=content.get('last_name'),
        vcard=content.get('vcard'),
    )
