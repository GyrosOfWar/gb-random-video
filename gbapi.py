"""A wrapper for the Giant Bomb API."""
from urllib.request import urlopen
from urllib.parse import urlencode
import json

def filter_empty(dictionary):
    """Removes all key-value pairs where the value is empty."""
    return dict((k, v) for k, v in dictionary.items() if v)


class GBApi():
    """A representation of the Giant Bomb API."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.video_types = {}

        # Get all the video types from the API
        base_url = 'http://www.giantbomb.com/api/video_types/?'
        params = {'format': 'json', 'api_key': self.api_key}
        types_url = base_url + urlencode(params)
        types_data = self.load_into_dict(types_url)
        # Store the video types in a map that maps the
        # name (e.g. quick_looks) to the type ID
        for _type in types_data['results']:
            t_name = _type['name'].lower().replace(' ', '_')
            t_id = _type['id']
            self.video_types[t_name] = t_id

        # Stores the number of available videos for each type of video
        self.video_counts = {}
        # A cache to store the API data in memory.
        self.cache = {}

    def load_into_dict(self, url):
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
        data = self.load_into_dict(url)

        count = data['number_of_total_results']
        if category_name:
            self.video_counts[category_name] = count
        else:
            self.video_counts['all'] = count

        return data['results']

    def all_videos(self, category_name):
        """Returns all videos from the given category."""
        if category_name and category_name not in self.video_types:
            raise ValueError('invalid video type: %s' % category_name)
        if not category_name:
            category_name = 'all'

        if category_name in self.cache:
            return self.cache[category_name]

        count = None
        cat = self.video_counts.get(category_name)
        if not cat:
            self.videos(video_type=category_name)
            cat = self.video_counts.get(category_name)
        count = cat

        all_results = []
        for offset in range(0, count, 100):
            if category_name:
                result = self.videos(offset=offset, video_type=category_name)
            else:
                result = self.videos(offset=offset)
            print("Fetching page with offset ", offset)
            all_results.extend(result)

        self.cache[category_name] = all_results
        return all_results