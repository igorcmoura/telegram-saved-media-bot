import os

from elasticsearch import Elasticsearch


INDEX_NAME = os.getenv('ES_INDEX_NAME')
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

client = Elasticsearch()
indices = client.indices

if indices.exists(INDEX_NAME):
    temp_index = INDEX_NAME + '_temp'
    if indices.exists(temp_index):
        raise RuntimeError('Temporary index already exists')

    indices.create(temp_index, body={'mappings': INDEX_MAPPING})
    client.reindex(
        {
            'source': {'index': INDEX_NAME},
            'dest': {'index': temp_index},
        }
    )
    indices.delete(INDEX_NAME)

    # Return to original index
    indices.create(INDEX_NAME, body={'mappings': INDEX_MAPPING})
    client.reindex(
        {
            'source': {'index': temp_index},
            'dest': {'index': INDEX_NAME},
        }
    )
    indices.delete(temp_index)
