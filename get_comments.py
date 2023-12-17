import os
import yt_dlp
import json
import yaml
import logging
import logging.config

def download_comments(video_url):
    log.debug("Downloading comments for video: %s", video_url)
    
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'writeinfojson': True,
        'getcomments': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        comments = info_dict.get('comments', [])

    log.debug("Downloaded %d comments for video: %s", len(comments), video_url)
    return comments

def save_to_json(comments, output_file='comments.json'):
    log.info("Saving comments to JSON file: %s", output_file)
    
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(comments, json_file, ensure_ascii=False, indent=4)
    
    log.info("Comments saved to %s", output_file)

def print_comments(comments):
    log.info("Printing formatted comments:")
    
    print("\nFormatted Comments:")
    for comment in comments:
        comment_id = comment.get('id', '')
        timestamp = comment.get('timestamp', '')
        username = comment.get('author', '')
        text = comment.get('text', '')

        formatted_comment = f"[{comment_id}] : [{timestamp}] : [{username}] : {text}"
        print(formatted_comment)

def main():
    log.info("Starting the script.")

    video_url = input("Enter YouTube video URL or ID: ")
    log.debug("User input video URL or ID: %s", video_url)
    
    comments = download_comments(video_url)

    if comments:
        print_comments(comments)
        save_to_json(comments)
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


    main()
