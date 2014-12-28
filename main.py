from flask import Flask
from private_data import API_KEY
from urllib.request import urlopen
from urllib.parse import urlencode
import json
import random
import os
from gbapi import GBApi
from database import DatabaseAdapter


api = GBApi(API_KEY)
app = Flask(__name__, static_url_path='/static/')
db = DatabaseAdapter('dbname=random_video')

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/random_video/<category>')
def random_video(category):
    """Returns a random video from a given category"""
    long_name = api.video_types_names.get(category)
    if not long_name:
        app.logger.error('Got invalid category name from internal API: %s' % category)
    videos = db.all_videos(long_name)
    idx = random.randint(0, len(videos))
    return videos[idx]


@app.route('/categories')
def categories():
    """Returns all of the video types."""
    return json.dumps(api.video_types_names)


@app.route('/static/<file_name>')
def static_files(file_name):
    return app.send_static_file(file_name)


if __name__ == '__main__':
    app.run(debug=True)
