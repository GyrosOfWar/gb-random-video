import psycopg2
from gbapi import GBApi
from private_data import API_KEY
from psycopg2.extras import Json

def first_time_setup():
    conn = psycopg2.connect('dbname=random_video user=postgres')
    cur = conn.cursor()
    cur.execute('CREATE TABLE video (id serial PRIMARY KEY, data json);')
    # TODO
    cur.execute('CREATE TABLE podcast (id serial PRIMARY KEY, title varchar, description varchar);')
    api = GBApi(API_KEY)
    for category in api.video_types.keys():
        print("Fetching category %s " % category)
        videos = api.all_videos(category)
        print("Inserting videos into DB")
        for video in videos:
            cur.execute('INSERT INTO video (data) VALUES (%s)', (Json(video),))
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
            #app.logger.error('Error writing to the database: %s' % err)

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
