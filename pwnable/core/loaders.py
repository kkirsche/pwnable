"""Loader handling functionality for PWNable.
Handles loading data to the local PWNable database or external databases such
as MySQL, PostgreSQL, Elasticsearch or Cassandra.
"""
# stdlib
from json import loads, dumps

# third party
from elasticsearch import Elasticsearch

# framework
from pwnable.core.helpers import color
from pwnable.modules.load.recon_ng import ReconNG


class Loaders(object):

    def __init__(self, main_menu, args=None):
        self.main_menu = main_menu
        self.conn = main_menu.conn

        self.es_client = None

        self.options = {
            'host': {
                'Description': 'Hostname/IP of the database server',
                'Required': True,
                'Value': '127.0.0.1'
            },
            'database': {
                'Description': 'Name of the database to load (Elasticsearch)',
                'Required': True,
                'Value': 'Elasticsearch'
            },
            'port': {
                'Description': 'The port which the database runs on',
                'Required': True,
                'Value': 9200
            },
            'format': {
                'Description': 'The format of the data (recon-ng)',
                'Required': True,
                'Value': 'recon-ng'
            }
        }

    def do_set(self, params):
        '''Sets the module options'''
        options = params.split()

        key = options[0].lower()
        if key in self.options:
            value = ' '.join(options[1:])
            if key == 'database':
                if value.lower() not in ['elasticsearch']:
                    print('[!] Invalid database')
                    return False
            if key == 'port':
                try:
                    value = int(value)
                except ValueError:
                    print('[!] Invalid port number')
                    return False
            self.options[key.lower()]['Value'] = value
            print('{k} => {v}'.format(k=key, v=value))
        else:
            print(color('[!] Invalid option'))

    def do_show(self, params):
        if params.lower() in self.options:
            k = params.lower()
            print('{k} => {v}'.format(k=k, v=self.options[k]['Value']))
        else:
            for k in self.options:
                print('{k} => {v}'.format(k=k, v=self.options[k]['Value']))

    def do_run(self, params):
        if self.options['database']['Value'].lower() == 'elasticsearch':
            return self.load_elasticsearch(params=params)

        print('[!] Unknown database. Aborting load...')

    def load_elasticsearch(self, params):
        try:
            self.es_client = Elasticsearch(
                [self.options['host']['Value']],
                port=self.options['port']['Value'])
        except Exception:
            print(
                color(
                    string='[!] Failed to connect to ElasticSearch',
                    color='red'))
            return False
        if self.options['format']['Value'] == 'recon-ng':
            self.load_elasticsearch_recon_ng(params=params)

    def load_elasticsearch_recon_ng(self, params):
        print(color('[*] Loading recon-ng data into ElasticSearch...'))
        try:
            self.recon_ng = ReconNG()
            if self.recon_ng.create_elasticsearch_index(self.es_client):
                paths = params.split()
                i = 0
                for path in paths:
                    with open(path, 'r') as f:
                        content = f.read()
                        content = loads(content)
                    for doc_type in content:
                        for item in content[doc_type]:
                            res = self.recon_ng.load_elasticsearch_item(
                                client=self.es_client,
                                doc_type=doc_type,
                                item=item)
                            if res:
                                i += 1
                            else:
                                i -= 1

                print(color('[*] {n} records loaded'.format(n=i), 'green'))
        except Exception as e:
            print(
                color(
                    '[!] Failed to load records into Elasticsearch due to an error. Is the database running?',
                    'red'))
