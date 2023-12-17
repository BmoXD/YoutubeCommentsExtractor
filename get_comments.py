import yt_dlp
import json

def download_comments(video_url):
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'writeinfojson': True,
        'getcomments': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        comments = info_dict.get('comments', [])

    return comments

def save_to_json(comments, output_file='comments.json'):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(comments, json_file, ensure_ascii=False, indent=4)
    print(f'Comments saved to {output_file}')

def print_comments(comments):
    print("\nFormatted Comments:")
    for comment in comments:
        comment_id = comment.get('id', '')
        timestamp = comment.get('timestamp', '')
        username = comment.get('author', '')
        text = comment.get('text', '')

        formatted_comment = f"[{comment_id}] : [{timestamp}] : [{username}] : {text}"
        print(formatted_comment)

def main():
    video_url = input("Enter YouTube video URL or ID: ")
    comments = download_comments(video_url)

    if comments:
        print_comments(comments)

        save_to_json(comments)
    else:
        print("No comments found for the given video.")

if __name__ == "__main__":
    main()