import logging

from telegram import Update, InlineQueryResultCachedAudio
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from ..common import filter_dict_none
from ..document import Document, DocumentType
from .common import ADDING_KEYWORDS_STATE, DOCUMENT_TO_INDEX_KEY
from .inline_search import inline_result_creator

logger = logging.getLogger(__name__)


def new_audio(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'User {user.id} sent an audio for indexing.')

    audio = update.message.audio
    if not audio.title:
        update.effective_chat.send_message(text='Invalid audio file, it must have a title metadata.')
        return ConversationHandler.END

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

    doc = Document(
        user_id=user.id,
        doc_type=DocumentType.AUDIO,
        content=content,
    )
    context.chat_data[DOCUMENT_TO_INDEX_KEY] = doc

    update.effective_chat.send_message(text='Now send me keywords to index this audio.')
    return ADDING_KEYWORDS_STATE


@inline_result_creator(DocumentType.AUDIO)
def create_audio_inline_result(id: str, doc: Document):
    content = doc.content
    return InlineQueryResultCachedAudio(
        id=id,
        audio_file_id=content['file_id'],
        caption=content.get('caption'),
    )


new_audio_handler = MessageHandler(Filters.audio, new_audio)
