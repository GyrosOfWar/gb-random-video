import psycopg2
from gbapi import GBApi, RssFeed
from private_data import API_KEY
from psycopg2.extras import Json

def first_time_setup_video():
    """Sets up the database and adds all the videos from the video API to it."""
    conn = psycopg2.connect('dbname=random_video')
    cur = conn.cursor()
    cur.execute('CREATE TABLE video (id serial PRIMARY KEY, data json);')
    api = GBApi(API_KEY)
    for category in api.video_types.keys():
        print("Fetching category %s " % category)
        videos = api.all_videos(category)
        print("Inserting videos into DB")
        for video in videos:
            cur.execute('INSERT INTO video (data) VALUES (%s)', (Json(video),))

    conn.commit()
    conn.close()

def first_time_setup_podcast(feed_url):
    conn = psycopg2.connect('dbname=random_video')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE podcast
    (id serial PRIMARY KEY,
    title text, 
    link text,
    description text,
    pub_date date);""")

    feed = RssFeed(feed_url)

    for item in reversed(feed.items):
        cur.execute("""
            INSERT INTO podcast (title, link, description, pub_date)
            VALUES (%s, %s, %s, %s)""",
                    (item.title, item.link,
                     item.description, item.pub_date))
    conn.commit()
    conn.close()


class DatabaseAdapter(object):
    """A thin abstraction layer to make common database operations for this app easier"""
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def insert_video(self, json_obj):
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO video (data) VALUES (%s)', (Json(json_obj),))
        except psycopg2.Error as err:
            print('Error writing to the database:', err)

        conn.commit()
        conn.close()

    def insert_podcast_item(self, feed_item):
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()

        try:
            cur.execute("""
            INSERT INTO podcast (title, link, description, pub_date)
            VALUES (%s, %s, %s, %s)""",
                        (feed_item.title, feed_item.link,
                         feed_item.description, feed_item.pub_date))
        except psycopg2.Error as err:
            print('Error inserting into the database:', err)

        conn.commit()
        conn.close()

    def all_video_urls(self, category):
        """Returns all the videos stored in the database for the given
        long category string name."""
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        videos = None
        try:
            cur.execute("SELECT data->'site_detail_url' FROM video WHERE data->>'video_type' = %s;",
                        (category,))
            videos = cur.fetchall()
        except psycopg2.Error as err:
            print('Error writing to the database:', err)

        if not videos:
            print('Was not able to find any videos for category', category)

        conn.close()
        return videos

    def all_videos_by_name(self, name):
        """Returns all the videos stored in the database that match with their name."""
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        videos = None
        try:
            name = '%' + name + '%'
            cur.execute("SELECT data->>'site_detail_url' FROM video WHERE data->>'name' LIKE %s;",
                        (name,))
            videos = [v[0] for v in cur.fetchall()]
        except psycopg2.Error as err:
            print('Error writing to the database:', err)

        if not videos:
            print('Was not able to find any videos matching the name', name)

        conn.close()
        return videos


    def has_video(self, video_id):
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        has_video = False

        try:
            cur.execute("""
            SELECT data->'id'
            FROM video
            WHERE (data->>'id')::int = %s;""",
                        (video_id,))
            has_video = cur.fetchone() != None

        except psycopg2.Error as err:
            print('Error querying the database:', err)
        conn.close()

        return has_video

    def has_podcast(self, podcast_name):
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        has_podcast = False
        try:
            cur.execute("""
            SELECT title 
            FROM podcast
            WHERE title = %s""",
                        (podcast_name,))
            has_podcast = cur.fetchone() != None

        except psycopg2.Error as err:
            print('Error querying the database:', err)

        conn.close()
        return has_podcast
