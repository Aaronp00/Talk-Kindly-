import googleapiclient.discovery
import re

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    pattern = r"(?<=v=)[\w-]+"
    match = re.search(pattern, url)
    if match:
        return match.group(0)
    else:
        return None

# Function to retrieve comments from YouTube API
def get_comments(youtube, video_id):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )
    response = request.execute()

    # Get the comments from the initial response
    for item in response['items']:
        comment_data = item['snippet']['topLevelComment']['snippet']
        author_display_name = comment_data['authorDisplayName']
        author_channel_id = comment_data['authorChannelId']['value'] if 'authorChannelId' in comment_data else None
        published_at = comment_data['publishedAt']
        text_original = comment_data['textOriginal']
        public = item['snippet']['isPublic']
        comments.append({
            'author_display_name': author_display_name,
            'author_channel_id': author_channel_id,
            'published_at': published_at,
            'text_original': text_original,
            'public': public
        })
    # Loop through pagination to get all comments
    while 'nextPageToken' in response:
        next_page_token = response['nextPageToken']
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response['items']:
            comment_data = item['snippet']['topLevelComment']['snippet']
            author_display_name = comment_data['authorDisplayName']
            author_channel_id = comment_data['authorChannelId']['value'] if 'authorChannelId' in comment_data else None
            published_at = comment_data['publishedAt']
            text_original = comment_data['textOriginal']
            public = item['snippet']['isPublic']
            comments.append({
                'author_display_name': author_display_name,
                'author_channel_id': author_channel_id,
                'published_at': published_at,
                'text_original': text_original,
                'public': public
            })

    return comments
