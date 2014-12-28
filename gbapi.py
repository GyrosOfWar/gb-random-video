"""A wrapper for the Giant Bomb API."""
from urllib.request import urlopen
from urllib.parse import urlencode
import json
import xml.etree.ElementTree as ET

def filter_empty(dictionary):
    """Removes all key-value pairs where the value is empty."""
    return dict((k, v) for k, v in dictionary.items() if v)

def load_into_dict(url):
    """Loads JSON from the given URL, parses it
       and stores it in a Python dict."""
    reply = urlopen(url)
    json_string = reply.readall().decode()
    return json.loads(json_string)

class GBApi(object):
    """A representation of the Giant Bomb API."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.video_types = {}

        # Get all the video types from the API
        base_url = 'http://www.giantbomb.com/api/video_types/?'
        params = {'format': 'json', 'api_key': self.api_key}
        types_url = base_url + urlencode(params)
        types_data = load_into_dict(types_url)
        # Store the video types in a map that maps the
        # name (e.g. quick_looks) to the type ID
        self.video_types = dict()
        for _type in types_data['results']:
            t_name = _type['name'].lower().replace(' ', '_')
            t_id = _type['id']
            self.video_types[t_name] = t_id

        # Stores the number of available videos for each type of video
        self.video_counts = dict()
        # A cache to store the API data in memory.
        self.cache = dict()

    def videos(self, **kwargs):
        """Represents the /videos/-API endpoint.
        Filter arguments:
        id: Numerical ID of the video
        name: Name of the video
        publish_date: Published date of the video.
        video_type: Name of the category of the video. (see video_types)"""
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
        data = load_into_dict(url)

        count = data['number_of_total_results']
        if category_name:
            self.video_counts[category_name] = count
        else:
            self.video_counts['all'] = count

        return data['results']

    def all_videos(self, category_name='all', refresh=False):
        """Returns all videos from the given category."""
        if category_name not in self.video_types:
            raise ValueError('invalid video type: %s' % category_name)

        # Look up the category in the cache
        if category_name in self.cache:
            return self.cache[category_name]

        # Try to get the number of videos for the given type
        count = self.video_counts.get(category_name)
        if not count:
            # Query the API for the number of videos
            self.videos(video_type=category_name, limit=1)
            count = self.video_counts.get(category_name)

        all_results = []
        # Fetch all of the videos from the API.
        # Each API query can at most retrieve 100 videos,
        # so increment the offset by 100 each iteration.
        for offset in range(0, count, 100):
            if category_name != 'all':
                result = self.videos(offset=offset, video_type=category_name)
            else:
                result = self.videos(offset=offset)

            all_results.extend(result)

        self.cache[category_name] = all_results
        return all_results

class RssFeed(object):
    """Represents a RSS feed. Stores the root of the
       XML tree of the RSS file and the feed's URL."""
    def __init__(self, feed_url):
        self.feed_url = feed_url
        xml = urlopen(feed_url).readall().decode()
        self.root = ET.fromstring(xml)

    def items(self):
        """Returns an iterator of all the feed items."""
        return self.root.iter('item')

    def item(self, i):
        """Returns the i-th RSS feed item."""
        return list(self.items())[i]
