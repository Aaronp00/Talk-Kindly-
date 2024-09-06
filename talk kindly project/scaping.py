# import pandas as pd
# from ntscraper import Nitter

# # Create a Nitter scraper instance
# scraper = Nitter()

# value = input("Please enter a Twitter user:\n")

# user = value 
# print(f'You entered Twitter user: {user}\n')

# # Define a function to get tweets from the specified user
# def get_tweets(name, modes, no):
#     final_tweets = []
#     tweets = scraper.get_tweets(name, mode=modes, number=no)
#     # Extract tweet data and store in a list of lists
#     for tweet in tweets['tweets']:
#         data = [tweet['link'], tweet['text'], tweet['date']]
#         final_tweets.append(data)
#     # Convert the list of lists into a DataFrame
#     data = pd.DataFrame(final_tweets, columns= ['Link', 'Text', 'Date']) 
#     return data

# # Call the function to get tweets
# data = get_tweets(user, 'user', 5)
# print(data)


from flask import Flask, render_template, request, redirect, url_for
import snscrape.modules.twitter as tw
from snscrape.base import ScraperException
from reddit_api import get_top_posts 
from reddit_api import get_reddit_client 
from reddit_api import search_inappropriate_words
import googleapiclient.discovery
import googleapiclient.errors
from youtube_api import get_comments, extract_video_id
from prawcore.exceptions import BadRequest , NotFound , Redirect
from email.message import EmailMessage
import ssl
import smtplib


app = Flask(__name__)




##################################Home 
@app.route('/')
def home():
   return render_template('home.html')


##################################how to use us 
@app.route('/Use_us')
def Use_us():
    return render_template('Use_us.html')


##################################About us 
@app.route('/About_us')
def About_us():
    return render_template('About_us.html')

########################### for Report email

@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        email_sender = 'talk.kindly24@gmail.com'
        email_password = 'jnmm mwwc nghr aauq'
        email_receiver = 'talk.kindly24@gmail.com'
        subject = "Talk Kindly Alert (New word request)"
        body = request.form['email_body']

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls(context=context)  # Enable TLS encryption
            smtp.login(email_sender, email_password)
            smtp.send_message(em)

        return redirect(url_for('email_confirmation'))

    return render_template('email_form.html')

@app.route('/email_confirmation')
def email_confirmation():
    return render_template('email_confirmation.html')



################################################ for youtube


#main youtube route 
@app.route('/youtube')
def Youtube():
    return render_template('youtube.html')

# The YouTube API
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyDH08ZSBh4O2p1ljUPiI3usvWu9ipWNeAE"  # my YouTube API key
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

@app.route('/youtube_results', methods=['POST'])
def youtube_results():
    youtube_url = request.form['youtube_url']
    video_id = extract_video_id(youtube_url)
    if video_id:
        comments = get_comments(youtube, video_id)
        # Check for inappropriate words in each comment
        for comment in comments:
            if search_inappropriate_words(comment['text_original']):
                comment['contains_inappropriate_words'] = True
            else:
                comment['contains_inappropriate_words'] = False

        return render_template('youtube_results.html', comments=comments)
    else:
        error_message = "Invalid YouTube URL or video ID not found."
        return render_template('error.html', error_message=error_message)




##############################################for Reddit 

# main  reddit route
@app.route('/reddit', methods=['GET', 'POST'])
def reddit():
        if request.method == 'POST':
            subreddit_name = request.form['subreddit']
            # Redirect to the /reddit_results route with the subreddit name as a query parameter
            return redirect(url_for('reddit_results', subreddit=subreddit_name))
        return render_template('reddit.html')

# the error handerlers for the reddit code , just incase  the wrong input is chosen 
@app.errorhandler(Redirect)
def handle_redirect_error(error):
    error_message = "Redirect error: Redirected to /subreddits/search"
    return render_template('error.html', error_message=error_message), 400

@app.errorhandler(BadRequest)
def handle_bad_request_error(error):
    error_message = "Bad request: The server received an invalid request."
    return render_template('error.html', error_message=error_message), 400

@app.errorhandler(NotFound)
def handle_not_found_error(error):
    error_message = "Not found: The requested resource could not be found."
    return render_template('error.html', error_message=error_message), 404

# Function to fetch top Reddit posts and flag posts with inappropriate words
def get_top_posts_flagged(subreddit_name, limit=100):
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)
    top_posts = []
    for post in subreddit.top(limit=limit):
        # Check for inappropriate words in the post title
        inappropriate_words = search_inappropriate_words(post.title)
        if inappropriate_words:
            post.has_inappropriate_words = True
        else:
            post.has_inappropriate_words = False
        top_posts.append(post)
    return top_posts

@app.route('/reddit_results')
def reddit_results():
    subreddit_name = request.args.get('subreddit')
    # Calling  the function to get top posts from Reddit with flagging
    top_posts = get_top_posts_flagged(subreddit_name, limit=500)
    return render_template('reddit_results.html',subreddit=subreddit_name, top_posts=top_posts)

######################################For twitter
# main twitter( X ) route
@app.route('/index')
def index():
   return render_template('index.html')

@app.route('/index.find')
def index_find():
   return render_template('index_find.html')


@app.route('/user', methods=['POST'])
def get_user():

    user = request.form['username']

    if not user or ' ' in user:
        error_message = "Invalid username."
        return render_template('user_not_found.html', error_message=error_message)

    try:
        results = tw.TwitterUserScraper(user)._get_entity()
        if results:
            # User found, render user template
            profile_image_banner_url = results.profileBannerUrl
            profile_image_url = results.profileImageUrl
            return render_template('user.html', user = results, profile_image_url=profile_image_url ,profile_image_banner_url = results.profileBannerUrl)
        else:
            # User not found, render user_not_found template
            return render_template('user_not_found.html')
    except ScraperException as e:
        # Handle empty response or other scraper exceptions
        return render_template('user_not_found.html', error_message=str(e))
    
    
   

if __name__ == '__main__':
    app.run(debug=True)

 # app.run(host='192.168.1.80', port=5000)