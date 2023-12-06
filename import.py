import csv
import re
import json
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
import html  # Used for decoding HTML entities

# Configuration
slack_token = os.getenv('SLACK_TOKEN')  # Replace with your Slack token from .env
channel_id = os.getenv('CHANNEL_ID')    # Replace with your Slack channel ID from .env
output_filename = 'slack_links.csv'
users_cache_file = 'users_cache.json'
messages_cache_file = 'messages_cache.json'

def load_exclusion_patterns(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Load exclusion patterns from a file
exclusion_patterns = load_exclusion_patterns('exclusion_patterns.txt')

# Initialize Slack client
client = WebClient(token=slack_token)

# Function to load cache from JSON file
def load_cache(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Function to save cache to JSON file
def save_cache(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file)

# Load caches
user_cache = load_cache(users_cache_file)
messages_cache = load_cache(messages_cache_file)

def fetch_all_messages(channel):
    if channel in messages_cache:
        return messages_cache[channel]

    messages = []
    print(f"Fetching messages from channel: {channel}")
    try:
        response = client.conversations_history(channel=channel)
        messages.extend(response['messages'])

        while response['has_more']:
            cursor = response['response_metadata']['next_cursor']
            print("Fetching next set of messages...")
            response = client.conversations_history(channel=channel, cursor=cursor)
            messages.extend(response['messages'])

    except SlackApiError as e:
        print(f"Error fetching messages: {e}")

    messages_cache[channel] = messages
    save_cache(messages_cache, messages_cache_file)
    print(f"Total messages fetched: {len(messages)}")
    return messages

def get_user_name(user_id):
    if user_id in user_cache:
        return user_cache[user_id]

    try:
        print(f"Fetching user name for ID: {user_id}")
        response = client.users_info(user=user_id)
        user = response.get('user', {})

        user_name = user.get('real_name') or user.get('name', "Unknown User")
        user_cache[user_id] = user_name  # Cache the user name
        save_cache(user_cache, users_cache_file)
        return user_name
    except SlackApiError as e:
        print(f"Error fetching user info: {e}")
        return "Unknown User"

def convert_timestamp_to_iso8601(unix_timestamp):
    return datetime.fromtimestamp(float(unix_timestamp)).isoformat()

def is_excluded_url(url):
    return any(pattern in url for pattern in exclusion_patterns)

def resolve_user_mentions(text):
    mention_pattern = r'<@(\w+)>'
    mentions = re.findall(mention_pattern, text)
    for user_id in mentions:
        user_name = get_user_name(user_id)
        text = text.replace(f"<@{user_id}>", f"@{user_name}")
    return text

def extract_actual_url(url):
    # Split the URL if it's in the format <URL|Displayed Text>
    if '|' in url:
        url = url.split('|')[0]
    return url

def extract_and_write_links(messages, filename):
    slack_url_pattern = r'<(https?://[^\s<>"]+|www\.[^\s<>"]+)(\|[^\s<>"]+)?>'
    print("Extracting links from messages and writing to CSV...")

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['created', 'user', 'url', 'note', 'tags','folder'])

        for message in messages:
            matches = re.findall(slack_url_pattern, message.get('text', ''))
            for match in matches:
                url = extract_actual_url(match[0])
                if not is_excluded_url(url):
                    user_name = get_user_name(message.get('user'))
                    timestamp = convert_timestamp_to_iso8601(message.get('ts'))
                    note = resolve_user_mentions(html.unescape(message.get('text')))
                    # Include the 'novu-developers' tag for each row
                    writer.writerow([timestamp, user_name, url, note, 'novu-developers', 'Dev'])

    print("Data export completed successfully.")

# Main execution
messages = fetch_all_messages(channel_id)
extract_and_write_links(messages, output_filename)