import logging
from typing import Callable, Dict

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.inlinequeryhandler import InlineQueryHandler
from telegram.inline.inlinequeryresult import InlineQueryResult

from ..es_store import store
from ..document import Document, DocumentType

logger = logging.getLogger(__name__)


class InlineResultCreatorLoader:
    def __init__(self):
        self._creators: Dict[DocumentType, Callable[[Document], InlineQueryResult]] = {}

    def get_for(self, doc_type: DocumentType) -> Callable[[Document], InlineQueryResult]:
        return self._creators[doc_type]

    def decorator(self, doc_type: DocumentType):
        def decorator(fn: Callable[[Document], InlineQueryResult]):
            self._creators[doc_type] = fn
            return fn
        return decorator


def inline_search(update: Update, context: CallbackContext):
    user = update.inline_query.from_user
    logger.info(f'User {user.id} is querying a document.')

    query = update.inline_query.query
    if query:
        store_results = store.search(user_id=user.id, keywords=query)
    else:
        store_results = store.get_all(user_id=user.id)

    results = [
        inline_result_creators.get_for(doc.doc_type)(id=str(idx), doc=doc)
        for idx, doc in enumerate(store_results)
    ]
    context.bot.answer_inline_query(update.inline_query.id, results, is_personal=True)


inline_result_creators = InlineResultCreatorLoader()
inline_result_creator = inline_result_creators.decorator

inline_search_handler = InlineQueryHandler(inline_search)
