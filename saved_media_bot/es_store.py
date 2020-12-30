from typing import Dict, Iterable
from elasticsearch import Elasticsearch

from .common import filter_dict_none
from .document import Document, DocumentType


class ElasticsearchStore:
    INDEX_NAME = 'telegram-saved-media-bot'
    INDEX_MAPPING = {
        'properties': {
            'user_id': {'type': 'keyword'},
            'type': {'type': 'keyword'},
            'keywords': {'type': 'search_as_you_type'}
        }
    }

    def __init__(self):
        self._client = Elasticsearch()

        indices = self._client.indices
        if not indices.exists(self.INDEX_NAME):
            indices.create(
                self.INDEX_NAME,
                body={'mappings': self.INDEX_MAPPING}
            )

    def save(self, doc: Document) -> None:
        es_doc = filter_dict_none({
            'user_id': doc.user_id,
            'type': doc.doc_type.value,
            'keywords': doc.keywords,
            'content': doc.content,
        })
        self._client.index(index=self.INDEX_NAME, body=es_doc)

    def get_all(self, user_id: str) -> Iterable[Document]:
        res = self._client.search(
            index=self.INDEX_NAME,
            body={
                'query': {'bool': {'filter': {'term': {'user_id': user_id}}}}
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
                }
            }
        )
        return self._get_docs_from_response(res)

    @staticmethod
    def _get_docs_from_response(response: Dict) -> Iterable[Document]:
        es_docs = ((doc['_id'], doc['_source']) for doc in response['hits']['hits'])
        return (
            Document(
                internal_id=doc_id,
                doc_type=DocumentType(doc['type']),
                user_id=doc['user_id'],
                keywords=doc['keywords'],
                content=doc['content']
            )
            for doc_id, doc in es_docs
        )


store = ElasticsearchStore()
