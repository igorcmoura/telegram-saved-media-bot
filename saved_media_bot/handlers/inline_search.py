from datetime import datetime
import logging
from typing import Callable, Dict

from telegram import Update, InlineQueryResult
from telegram.ext import CallbackContext, ChosenInlineResultHandler, InlineQueryHandler

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
    inline_query = update.inline_query
    user = inline_query.from_user
    logger.info(f'User {user.name}({user.id}) is querying a document.')

    query = inline_query.query
    if query:
        store_results = store.search(user_id=user.id, keywords=query)
    else:
        store_results = store.get_all(user_id=user.id)

    results = [
        inline_result_creators.get_for(doc.doc_type)(doc)
        for doc in store_results
    ]
    inline_query.answer(
        results=results,
        is_personal=True,
        cache_time=0,
        auto_pagination=True,
    )


def update_last_used_at(update: Update, context: CallbackContext):
    user = update.chosen_inline_result.from_user
    logger.info(f'User {user.name}({user.id}) selected a query result. Updating last used date.')

    doc_id = update.chosen_inline_result.result_id
    doc = store.get(doc_id)
    doc.last_used_at = datetime.now()
    store.update(doc_id, doc)


inline_result_creators = InlineResultCreatorLoader()
inline_result_creator = inline_result_creators.decorator

inline_search_handler = InlineQueryHandler(inline_search)
chosen_inline_result_handler = ChosenInlineResultHandler(update_last_used_at)
