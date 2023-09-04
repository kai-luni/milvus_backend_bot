from datetime import datetime, timedelta
import os
import openai
import praw
import time

from rocketchat_API.rocketchat import RocketChat

from test_milvus_gpt.chat_utils import call_chatgpt_api

def initialize_openai():
    """
    Initialize the OpenAI settings using environment variables.

    This function configures the OpenAI SDK to use the "azure" type and sets up other necessary configurations
    using the environment variables. Make sure the required environment variables are set before calling this function.
    """
    openai.api_type = "azure"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_base = os.getenv('OPENAI_API_BASE')
    openai.api_version = os.getenv('OPENAI_API_VERSION')



client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")

# Initialize the Reddit instance
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='reddit_thread_reader')

# Initialize RocketChat instance
server_ip = os.getenv("SERVER_IP")
password_rocket = os.getenv("PW_ROCKET")
rocket = RocketChat('PhatGpt', password_rocket, server_url=f'http://{server_ip}:3000')
channel = 'reddit_ukraine'  # Replace with your Rocket.Chat channel name

initialize_openai()

while True:
    # Get the submission by URL
    submission = reddit.submission(url='https://www.reddit.com/r/worldnews/comments/169hhtt/rworldnews_live_thread_russian_invasion_of/')

    # Replace the "more" comments to fetch all top-level comments
    submission.comments.replace_more(limit=None)

    # Get the current time
    current_time = datetime.utcnow()

    # Filter top-level comments posted in the last 120 minutes and with a score greater than or equal to 1
    # Then sort them so that the newest comes first
    recent_top_level_comments = sorted([comment for comment in submission.comments if current_time - datetime.utcfromtimestamp(comment.created_utc) <= timedelta(minutes=120) and comment.score >= 1], key=lambda x: x.created_utc, reverse=True)

    chunks = []

    # Send the details of the recent top-level comments and their top 3 second-level comments to Rocket.Chat
    for top_comment in recent_top_level_comments:        
        human_readable_time_top = datetime.utcfromtimestamp(top_comment.created_utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        chunk = f"--- Top-Level Comment:\nAuthor: {top_comment.author}\nTime: {human_readable_time_top}\nScore: {top_comment.score}\n{top_comment.body}\n---\n"        
        #rocket.chat_post_message(top_comment_message, channel=channel)

        # Sort the second-level comments by score, take the top 3, and filter out those with a score less than 1
        top_replies = sorted([reply for reply in top_comment.replies if reply.score >= 1], key=lambda x: x.score, reverse=True)[:3]

        # Send the top 3 second-level comments for the current top-level comment to Rocket.Chat
        for reply in top_replies:
            human_readable_time_reply = datetime.utcfromtimestamp(reply.created_utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            chunk = chunk + f" Second-Level Comment:\nAuthor: {reply.author}\nTime: {human_readable_time_reply}\nScore: {reply.score}\n{reply.body}\n---\n"
            chunks.append(chunk)
            #rocket.chat_post_message(reply_message, channel=channel)
    print(''.join(chunks))
    response = call_chatgpt_api("------------\nsummarize the data above, its a reddit thread. List the different topics that was talked about and give preference to the higher score comments. Show the scores when you mention a comment. List all topic by importance.", [''.join(chunks)])
    rocket.chat_post_message(response["choices"][0]["message"]["content"], channel=channel)

    # Sleep for 30 minutes (1800 seconds) before the next iteration
    time.sleep(1800)
