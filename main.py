from flask import Flask
from private_data import API_KEY
from urllib.request import urlopen
from urllib.parse import urlencode
import json
import random
import os
from gbapi import GBApi


api = GBApi(API_KEY)
app = Flask(__name__, static_url_path='/static/')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/random_video/<category>')
def random_video(category):
    """Returns a random video from a given category"""
    videos = api.all_videos(category)
    idx = random.randint(0, len(videos))
    print(idx)
    url = videos[idx]['site_detail_url']
    return url

@app.route('/categories')
def categories():
    """Returns all of the video types."""
    categories = list(api.video_types.keys())
    category_map = dict()
    for i in range(0, len(categories)):
        c = categories[i]
        nice_name = c.replace('_', ' ').title()
        category_map[c] = nice_name
        return json.dumps(category_map)


@app.route('/static/<file_name>')
def static_files(file_name):
    return app.send_static_file(file_name)


if __name__ == '__main__':
    app.run()
