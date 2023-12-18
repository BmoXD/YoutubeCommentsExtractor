from configparser import ConfigParser
from datetime import datetime
import os
import yt_dlp
import json
import yaml
import logging
import logging.config
import mysql.connector

from mysql.connector import Error

video_url = ''
cookies = ''

# Connecting to the database
def init_db():
	global connection
	connection = mysql.connector.connect(host=mysql_host,
                                      database=mysql_db,
                                      user=mysql_user,
                                      password=mysql_pass)
    
def get_cursor():
	global connection
	try:
		connection.ping(reconnect=True, attempts=1, delay=0)
		connection.commit()
	except mysql.connector.Error as err:
		log.error("No connection to db " + str(err))
		connection = init_db()
		connection.commit()
	return connection.cursor()

def download_comments(video_url):
    log.debug("Downloading comments for video: %s", video_url)
    
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'writeinfojson': True,
        'getcomments': True,
    }

    video_data = {
    'channel_id': '',
    'video_id': '',
    'comments': []
    }

    # Check if cookies is not an empty string before adding it to ydl_opts
    if cookies:
        ydl_opts['cookiefile'] = cookies
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_data['comments'] = info_dict.get('comments', [])
            video_data['video_id'] = info_dict.get('id')
            video_data['channel_id'] = info_dict.get('channel_id')
            #log.debug(video_id)
            log.debug(info_dict)
    except:
        log.exception('')

    log.debug("Downloaded %d comments for video: %s", len(video_data['comments']), video_url)
    return video_data

def save_to_json(comments, output_file='comments.json'):
    log.info("Saving comments to JSON file: %s", output_file)
    
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(comments, json_file, ensure_ascii=False, indent=4)
    
    log.info("Comments saved to %s", output_file)

def print_comments(comments):
    log.info("Printing first 50 formatted comments:")
    
    print("\nFormatted Comments:")
    for comment in comments[:50]: # Printing only 50 comments per run
        comment_id = comment.get('id', '')
        timestamp = comment.get('timestamp', '')
        username = comment.get('author', '')
        comment_text = comment.get('text', '')

        formatted_comment = f"[{comment_id}] : [{timestamp}] : [{username}] : {comment_text}"
        log.debug(formatted_comment)

def save_to_db(video_data):
    global connection

    channel_id = video_data['channel_id']
    video_id = video_data['video_id']
    comments = video_data['comments']

    try:
        cursor = connection.cursor()

        # Checking if the table for the channel already exists
        #cursor.execute(f"SHOW TABLES LIKE '`{channel_id.lower()}`'")

        cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{channel_id}'")
        aaaa = cursor.fetchone()[0]
        print("adsadssadsad: "+ str(aaaa))
        if aaaa <= 0:
            log.info("This video of id ["+video_id+"] is from a channel of id ["+channel_id+"] never seen before. Creating new table!")
            # Create a new table for the specific video
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS `{channel_id}` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    video_id VARCHAR(255),
                    comment_id VARCHAR(255),
                    timestamp DATETIME,
                    username VARCHAR(255),
                    comment_text TEXT
                )
            """
            cursor.execute(create_table_query)
            connection.commit()

            log.info("Table "+ channel_id +" created successfully.")

        for comment in comments:
            comment_id = comment.get('id', '')

            # Check if the comment_id already exists in the table
            check_query = f"SELECT * FROM `{channel_id}` WHERE comment_id = %s"
            cursor.execute(check_query, (comment_id,))
            existing_comment = cursor.fetchone()

            if existing_comment:
                 log.info("Comment with comment_id ["+comment_id+"] already exists in the table. Skipping insertion.")
                 continue

            timestamp = comment.get('timestamp', '')
            formated_timestamp = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') # Unix time to human readable time
            username = comment.get('author', '')
            comment_text = comment.get('text', '')

            # Insert the comment into the MySQL database
            insert_query = f"""
                INSERT INTO `{channel_id}` (video_id, comment_id, timestamp, username, comment_text)
                VALUES (%s, %s, %s, %s, %s)
            """
            query_values = (video_id, comment_id, formated_timestamp, username, comment_text)
            cursor.execute(insert_query, query_values)
            connection.commit()

    except Error as e:
        log.error("Error: "+ str(e))

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            log.info("MySQL connection closed.")

def main():
    global video_url
    log.info("Starting the script.")

    if video_url == '':
        video_url = input("Enter YouTube video URL or ID: ")
        log.debug("User input video URL or ID: %s", video_url)
    
    video_data = download_comments(video_url)

    if video_data:
        print_comments(video_data['comments'])
        save_to_json(video_data['comments'])
        save_to_db(video_data)
    else:
        log.warning("No comments found for the given video.")

    log.info("Script execution completed.")

if __name__ == "__main__":

    # If log folder doesn't exist then create one!
    log_folder = 'log'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
        print(f"Created '{log_folder}' folder.")

    # Loading logging configuration
    with open('./log_comments.yaml', 'r') as stream:
        log_config = yaml.safe_load(stream)

    logging.config.dictConfig(log_config)
    
    log = logging.getLogger('root')
    
    try:
        config = ConfigParser()
        config.read('config.ini')

        # [youtube] section
        video_url = config.get('youtube', 'video_link').strip()
        cookies = config.get('youtube', 'cookies_file')

        # [mysql] section
        mysql_host = config.get('mysql', 'mysql_host')
        mysql_db = config.get('mysql', 'mysql_db')
        mysql_user = config.get('mysql', 'mysql_user')
        mysql_pass = config.get('mysql', 'mysql_pass')
    except:
        log.exception('')
    log.info("Done loading config.ini")

    # Let's connect to the database
    init_db()
    
    log.info('Connecting to MySQL DB')

    log.info('Connecting to MySQL DB')
    try:
        cursor = get_cursor()
        if connection.is_connected():
            db_Info = connection.get_server_info()
            log.info('Connected to MySQL database. MySQL Server version on ' + str(db_Info))
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            log.debug('Your connected to - ' + str(record))
            connection.commit()
    except Error as e :
        log.error('Error while connecting to MySQL' + str(e))


    main()
