from datetime import datetime
from typing import Dict, Iterable
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from .common import filter_dict_none
from .config import Config
from .document import Document, DocumentType


class ElasticsearchStore:
    INDEX_NAME = Config.ES_INDEX_NAME
    INDEX_MAPPING = {
        'properties': {
            'content': {'type': 'object', 'enabled': False},
            'created_at': {'type': 'date'},
            'last_used_at': {'type': 'date'},
            'user_id': {'type': 'keyword'},
            'type': {'type': 'keyword'},
            'keywords': {'type': 'search_as_you_type'}
        }
    }
    # TODO: find an optimal value that won't affect performance
    MAX_SEARCH_RESULTS = 10000

    def __init__(self):
        self._client = Elasticsearch()

        indices = self._client.indices
        if not indices.exists(self.INDEX_NAME):
            indices.create(
                self.INDEX_NAME,
                body={'mappings': self.INDEX_MAPPING}
            )

    def save(self, doc: Document) -> None:
        source = self._es_source_from_doc(doc)
        self._client.index(index=self.INDEX_NAME, body=source)

    def get(self, id: str) -> Document:
        es_doc = self._client.get(index=self.INDEX_NAME, id=id)
        source = es_doc['_source']
        return self._doc_from_es_source(source, id)

    def update(self, id: str, doc: Document) -> None:
        source = self._es_source_from_doc(doc)
        self._client.index(index=self.INDEX_NAME, id=id, body=source)

    def delete(self, id: str) -> None:
        try:
            self._client.delete(index=self.INDEX_NAME, id=id)
        except NotFoundError:
            # TODO maybe this should be handled correctly...
            pass

    def get_all(self, user_id: str) -> Iterable[Document]:
        res = self._client.search(
            index=self.INDEX_NAME,
            body={
                'query': {'bool': {'filter': {'term': {'user_id': user_id}}}},
                'sort': ['_score', {'last_used_at': 'desc'}],
                'size': self.MAX_SEARCH_RESULTS,
            }
        )
        return self._get_docs_from_response(res)

    def search(self, user_id: str, keywords: str) -> Iterable[Document]:
        res = self._client.search(
            index=self.INDEX_NAME,
            body={
                'query': {
                    'bool': {
                        'filter': {'term': {'user_id': user_id}},
                        'must': [{
                            'multi_match': {
                                'query': keywords,
                                'type': 'bool_prefix',
                                'fields': [
                                    'keywords',
                                    'keywords._2gram',
                                    'keywords._3gram'
                                ]
                            }
                        }]
                    }
                },
                'sort': ['_score', {'last_used_at': 'desc'}],
                'size': self.MAX_SEARCH_RESULTS,
            }
        )
        return self._get_docs_from_response(res)

    @classmethod
    def _get_docs_from_response(cls, response: Dict) -> Iterable[Document]:
        es_docs = ((doc['_id'], doc['_source']) for doc in response['hits']['hits'])
        for doc_id, source in es_docs:
            yield cls._doc_from_es_source(source, doc_id)

    @staticmethod
    def _doc_from_es_source(es_source: Dict, doc_id: str = None) -> Document:
        return Document(
            internal_id=doc_id,
            created_at=datetime.fromtimestamp(es_source['created_at']),
            last_used_at=datetime.fromtimestamp(es_source['last_used_at']),
            doc_type=DocumentType(es_source['type']),
            user_id=es_source['user_id'],
            keywords=es_source['keywords'],
            content=es_source['content']
        )

    @staticmethod
    def _es_source_from_doc(doc: Document) -> Dict:
        return filter_dict_none({
            'created_at': doc.created_at.timestamp(),
            'last_used_at': doc.last_used_at.timestamp(),
            'user_id': doc.user_id,
            'type': doc.doc_type.value,
            'keywords': doc.keywords,
            'content': doc.content,
        })


store = ElasticsearchStore()
