from dataclasses import dataclass
from enum import Enum
from typing import Dict, Union


class DocumentType(Enum):
    AUDIO = 'audio'
    ANIMATION = 'animation'
    CONTACT = 'contact'
    DOCUMENT = 'document'
    LOCATION = 'location'
    PHOTO = 'photo'
    STICKER = 'sticker'
    VIDEO = 'video'
    VOICE = 'voice'


@dataclass
class Document:
    user_id: str
    doc_type: DocumentType
    content: Dict
    internal_id: Union[str, None] = None
    keywords: Union[str, None] = None
