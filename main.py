from flask import Flask
from private_data import API_KEY
from urllib.request import urlopen
import json

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
    
    def append_api_key(self, url):
        return url + '&api_key=' + self.api_key
        
    def load_into_dict(url):
        reply = urlopen(url)
        json_string = reply.readall().decode()
        return json.loads(json_string)

    def videos(self, **kwargs):
        # possible query parameters:
        # id
        # name
        pass


app = Flask(__name__)
@app.route('/')
def hello():
    # TODO return a redirect to a random video in a given category
    return '<h1>Hello World!</h1>'


if __name__ == '__main__':
    app.run()
