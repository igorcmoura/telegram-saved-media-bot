from dataclasses import dataclass
from enum import Enum
from typing import Dict, Union


class DocumentType(Enum):
    AUDIO = 'audio'
    ANIMATION = 'animation'
    PHOTO = 'photo'


@dataclass
class Document:
    user_id: str
    doc_type: DocumentType
    content: Dict
    keywords: Union[str, None] = None
