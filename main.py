from flask import Flask
from private_data import API_KEY
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus
import json

def filter_empty(dictionary):
    return dict((k, v) for k, v in dictionary.items() if v)


class GBApi():
    def __init__(self, api_key):
        self.api_key = api_key
        self.video_types = {}
        types_url = self.append_api_key('http://www.giantbomb.com/api/video_types/?format=json')
        types_data = GBApi.load_into_dict(types_url)
        for _type in types_data['results']:
            t_name = _type['name'].lower().replace(' ', '_')
            t_id = _type['id']
            self.video_types[t_name] = t_id

        self.video_counts = {}
    
    def append_api_key(self, url):
        return url + '&api_key=' + self.api_key
        
    def load_into_dict(url):
        reply = urlopen(url)
        json_string = reply.readall().decode()
        return json.loads(json_string)

    def videos(self, **kwargs):
        #TODO write docstring
        video_id = kwargs.get('id')
        name = kwargs.get('name')
        date = kwargs.get('publish_date')
        # The argument passed in is the category string, the
        # API expects the video ID, so fetch the id from the map
        category_name = kwargs.get('video_type')
        video_type = None
        if category_name and category_name not in self.video_types:
            raise ValueError('Provided an invalid category name: %s' % category_name)
        video_type = self.video_types[category_name]
        offset = kwargs.get('offset')
        limit = kwargs.get('limit')
  
        filters = filter_empty({'id': video_id, 'name': name,
                                'publish_date': date, 'video_type': video_type})
        filter_string = ''
        for field, value in filters.items():
            filter_string += '%s:%s,' % (field, value)

        args = filter_empty({'offset': offset, 'limit': limit, 'format': 'json',
                             'filter': filter_string, 'api_key': self.api_key})

        params = urlencode(args)
        url = 'http://www.giantbomb.com/api/videos/?%s' % params
        data = GBApi.load_into_dict(url)
        
        count = data['number_of_total_results']
        if category_name:
            self.video_counts[category_name] = count
        else:
            self.video_counts['all'] = count

        return data['results']

    def all_videos(self, category_name):
        as a lower case string, with spaces replaced by
        underscores.""
        if category_name and category_name not in self.video_types:
            raise ValueError('invalid video type: %s' % category)

        count = None
        if category_name:
            count = self.video_counts.get(category_name)
        else:
            count = self.video_counts.get('all')
        
        if not count:
            if category_name:
                self.videos(video_type=category_name)
            else:
                self.videos()

        if category_name:
            count = self.video_counts.get(category_name)
        else:
            count = self.video_counts.get('all')
        
        all_results = []
        for offset in range(0, count, 100):
            if category_name:
                result = self.videos(offset=offset, video_type=category_name)
            else:
                result = self.videos(offset=offset)
            all_results.extend(result)

        return all_results
        
    
app = Flask(__name__)
@app.route('/')
def hello():
    # TODO return a redirect to a random video in a given category
    return '<h1>Hello World!</h1>'


if __name__ == '__main__':
    app.run()
