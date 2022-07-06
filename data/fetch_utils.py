import os
import requests
import base64
import math
from io import BytesIO

from PIL import Image
from kvfile import KVFile

_cache = KVFile(filename='_cache_airtable')
override = set([])
for key in override:
    try:
        _cache.get(key)
        print('got', key)
        _cache.delete(key)
        print('deleted', key)
    except:
        print('no such key', key)
        pass

def fetch_airtable_aux(kind, rid=None, view='Grid%20view', offset=None):
    API_KEY = os.environ.get('AIRTABLE_API_KEY')
    HEADERS = {
        'Authorization': 'Bearer ' + API_KEY
    }
    URL = 'https://api.airtable.com/v0/appS26oaF2FevHUzY/' + kind
    if rid:
        URL +=  '/' + rid
        print(URL)
        ret = requests.get(URL, headers=HEADERS).json()['fields']
    else:
        URL += f'?view={view}'
        if offset:
            URL += f'&offset={offset}'
        print(URL)
        resp = requests.get(URL, headers=HEADERS).json()
        ret = [x['fields'] for x in resp['records']], resp.get('offset')
    return ret


def fetch_airtable(kind, rid=None, view='Grid%20view'):
    key = '%s/%s' % (kind, rid)
    try:
        return _cache.get(key)
    except (KeyError, AssertionError):
        if rid:
            return fetch_airtable_aux(kind, rid=rid)
        else:
            ret = []
            offset = None
            while True:
                recs, offset = fetch_airtable_aux(kind, view=view, offset=offset)
                ret += recs
                if not offset:
                    break
        _cache.set(key, ret)
        return ret


def fetch_ckan(dataset, resource_name):
    API_KEY = os.environ.get('CKAN_API_KEY')
    CKAN_BASE = 'https://opendataprod.br7.org.il' + '/api/3/action'
    headers = {'Authorization': API_KEY}
    dataset = requests.get(f'{CKAN_BASE}/package_show?id={dataset}', headers=headers).json()
    assert dataset['success']
    dataset = dataset['result']
    for resource in dataset['resources']:
        if resource['name'] == resource_name:
            return requests.get(resource['url'], headers=headers, stream=True).raw
    print('Failed to find resource', resource)

def to_data_url(url, width=96):
    key = 'data-url:' + url
    try:
        return _cache.get(key)
    except KeyError:
        im = Image.open(requests.get(url, stream=True).raw)
        ratio = width/im.width
        im = im.resize((width, math.floor(im.height*ratio)))
        out = BytesIO()
        im.save(out, 'jpeg', quality=50, optimize=True)
        ret = 'data:image/jpeg;base64,{}'.format(base64.encodebytes(out.getbuffer()).decode('ascii').replace('\n', ''))
        _cache.set(key, ret)
        return ret
