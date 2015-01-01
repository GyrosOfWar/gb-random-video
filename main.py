from flask import Flask
from private_data import API_KEY
from urllib.request import urlopen
from urllib.parse import urlencode
import json
import random
import os
from gbapi import GBApi, RssFeed
from database import DatabaseAdapter


api = GBApi(API_KEY)
app = Flask(__name__, static_url_path='/static/')
db = DatabaseAdapter('dbname=random_video')
bombcast_feed = RssFeed('http://www.giantbomb.com/podcast-xml/giant-bombcast/')

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/random_video/<category>')
def random_video(category):
    """Returns a random video from a given category"""
    long_name = api.video_types_names.get(category)
    if not long_name:
        app.logger.error('Got invalid category name from internal API: %s' % category)
    videos = db.all_video_urls(long_name)
    idx = random.randint(0, len(videos))
    return videos[idx]


# TODO implement periodical updates for the feed
@app.route('/random_bombcast')
def random_bombcast():
    idx = random.randint(0, len(bombcast_feed.items))
    return bombcast_feed.items[idx].link


@app.route('/categories')
def categories():
    """Returns all of the video types."""
    return json.dumps(api.video_types_names)


@app.route('/static/<file_name>')
def static_files(file_name):
    return app.send_static_file(file_name)


def refresh_videos():
    new_videos = api.videos(limit=10)
    for v in new_videos:
        if not db.has_video(v['id']):
            db.insert_video(v)

def refresh_podcasts():
    bombcast_feed = RssFeed('http://www.giantbomb.com/podcast-xml/giant-bombcast/')
    for item in bombcast_feed.items:
        if not db.has_podcast(item.title):
            db.insert_podcast_item(item)

if __name__ == '__main__':
    app.run(debug=True)
