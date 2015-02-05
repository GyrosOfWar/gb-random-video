"""A wrapper for the Giant Bomb API."""
from urllib.request import urlopen
from urllib.parse import urlencode
import json
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import datetime

def filter_empty(dictionary):
    """Removes all key-value pairs where the value is empty."""
    return dict((k, v) for k, v in dictionary.items() if v)

def load_into_dict(url):
    """Loads JSON from the given URL, parses it
       and stores it in a Python dict."""
    reply = urlopen(url)
    json_string = reply.readall().decode()
    return json.loads(json_string)

def get_error(json_obj):
    error = json_obj['status_code']
    if error == 1:
        return 'OK'
    else:
        err_string = json_obj['error']
        print('Error querying the API:', err_string)
        return err_string


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
        self.video_types_names = dict()
        # TODO special case Metal Gear Scanlon videos
        # since those videos have both Subscriber
        # and Metal Gear Scanlon as category
        for _type in types_data['results']:
            long_name = _type['name']
            short_name = long_name.lower().replace(' ', '_')
            t_id = _type['id']
            self.video_types[short_name] = t_id
            self.video_types_names[short_name] = long_name

        # Stores the number of available videos for each type of video
        self.video_counts = dict()

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
        video_type = self.video_types.get(category_name)
        offset = kwargs.get('offset')
        limit = kwargs.get('limit')

        filters = filter_empty({'id': video_id, 'name': name,
                                'publish_date': date, 'video_type': video_type})
        filter_string = ''
        for field, value in filters.items():
            filter_string += '%s:%s,' % (field, value)

        args = filter_empty({'offset': offset, 'limit': limit, 'format': 'json',
                             'filter': filter_string, 'api_key': self.api_key})

        url = 'http://www.giantbomb.com/api/videos/?%s' % urlencode(args)
        data = load_into_dict(url)

        error = get_error(data)
        if error != 'OK':
            raise ValueError('Encountered error querying the API: %s' % error)

        count = data['number_of_total_results']
        if category_name:
            self.video_counts[category_name] = count
        else:
            self.video_counts['all'] = count

        return data['results']

    def all_videos(self, category_name='all'):
        """Returns all videos from the given category."""
        if category_name not in self.video_types:
            raise ValueError('invalid video type: %s' % category_name)

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

        return all_results

class RssFeed(object):
    """Represents a RSS feed. Stores the root of the
       XML tree of the RSS file and the feed's URL."""
    def __init__(self, feed_url):
        self.feed_url = feed_url
        xml = urlopen(feed_url).readall().decode()
        self.root = ET.fromstring(xml)
        self.items = []
        for item in self.root.iter('item'):
            title = item[0].text
            link = item[1].text
            description = item[2].text
            pub_date = parsedate_to_datetime(item[3].text)
            duration_string = item[9].text
            duration = None
            if duration_string:
                duration = int(duration_string)
            feed_item = RssFeedItem(title, link, description, pub_date, duration)
            self.items.append(feed_item)

    def item(self, i):
        """Returns the i-th RSS feed item."""
        return self.items[i]

    def __str__(self):
        return str(list(map(lambda i: i.title, self.items)))

class RssFeedItem(object):
    def __init__(self, title, link, description, pub_date, duration):
        self.title = title
        self.link = link
        self.description = description
        self.pub_date = pub_date
        self.duration = duration

    def __str__(self):
        return self.title
