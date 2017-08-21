from elasticsearch.exceptions import TransportError
from pwnable.core.helpers import color
from json import dumps, loads


class ReconNG:
    def __init__(self):
        self.hosts_mapping = {
            'properties': {
                'country': {
                    'type': 'keyword'
                },
                'region': {
                    'type': 'keyword'
                },
                'longitude': {
                    'type': 'float'
                },
                'latitude': {
                    'type': 'float'
                },
                'host': {
                    'type': 'keyword'
                },
                'module': {
                    'type': 'keyword'
                },
                'ip_address': {
                    'type': 'ip'
                },
                'geo_location': {
                    'type': 'geo_point'
                }
            }
        }

        self.contacts_mapping = {
            'properties': {
                'first_name': {
                    'type': 'keyword'
                },
                'last_name': {
                    'type': 'keyword'
                },
                'middle_name': {
                    'type': 'keyword'
                },
                'title': {
                    'type': 'text'
                },
                'country': {
                    'type': 'keyword'
                },
                'region': {
                    'type': 'keyword'
                },
                'module': {
                    'type': 'keyword'
                },
                'email': {
                    'type': 'keyword'
                }
            }
        }

        self.mapping = {
            'mappings': {
                'hosts': self.hosts_mapping,
                'contacts': self.contacts_mapping
            }
        }
        self.index_name = 'recon-ng'

    def create_elasticsearch_index(self, client):
        try:
            client.indices.create(index=self.index_name, body=self.mapping)
            return True
        except TransportError as e:
            # ignore already existing index
            if e.error == 'index_already_exists_exception':
                pass
                return True
            else:
                raise e
        except Exception as e:
            print(color('[!] Failed to create index due to an error {e}'.format(e=e)))
        return False

    def load_elasticsearch_item(self, client, doc_type, item):
        if 'latitude' in item and 'longitude' in item:
            item['geo_location'] = {
                'lat': item['latitude'],
                'lon': item['longitude']
            }
        res = client.index(index=self.index_name, doc_type=doc_type, body=item)
        if not res['created']:
            print(
                color(
                    '[!] Failed to load item {i}'.format(i=loads(item)), 'red'))
            return False
        return True
