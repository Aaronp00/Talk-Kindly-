

import praw
import re

def get_reddit_client():
    # Initialize Reddit client
    reddit = praw.Reddit(client_id='zQJZqTO2LrquwayowpDSKg',
                         client_secret='SYst4iK_kZdcLSKUV96x7dGOk9d0aA',
                         user_agent='YOUR_USER_AGENT')
    return reddit

def get_top_posts(subreddit_name, limit):
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)
    return subreddit.top(limit=limit)

# Function to search for inappropriate words in the given string
def search_inappropriate_words(string):
    # The path to the text file containing inappropriate words
    file_path = 'C:\me\project\Scaping\words_to_find.txt'
    
    # Reading the words from the text file
    with open(file_path, 'r') as file:
        words_to_find_from_file = [line.strip() for line in file]
    
    #  A regular expression pattern to match any of the words (case-insensitive)
    pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, words_to_find_from_file)))
    
    # Search for the words within the string (case-insensitive)
    word_matches = re.findall(pattern, string, re.IGNORECASE)
    
    return word_matches



# Example usage:
# subreddit_name = 'example_subreddit'
# #top_posts = get_top_posts(subreddit_name, limit=5)

# for post in top_posts:
#     print("Title:", post.title)
#     print("URL:", post.url)
#     print("--------")
    
    
    # # Search for inappropriate words in the post title
    # inappropriate_words = search_inappropriate_words(post.title)
    # if inappropriate_words:
    #     print("Inappropriate words found in title:", inappropriate_words)

 