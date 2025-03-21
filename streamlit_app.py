#v1
'''
import streamlit as st
import praw
import gspread
import datetime
import re
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication using Streamlit secrets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Streamlit UI
st.title("Reddit Scraper")

# Load saved input
if 'saved_url' not in st.session_state:
    st.session_state['saved_url'] = ""
if 'saved_keywords' not in st.session_state:
    st.session_state['saved_keywords'] = ""

# Input fields
url_input = st.text_area("Enter subreddit links (one per line)", value=st.session_state['saved_url'])
keyword_input = st.text_area("Enter keywords (comma-separated)", value=st.session_state['saved_keywords'])

# Buttons for actions
if st.button("Save Input"):
    st.session_state['saved_url'] = url_input
    st.session_state['saved_keywords'] = keyword_input
    st.success("Input saved.")

if st.button("Reset"):
    st.session_state['saved_url'] = ""
    st.session_state['saved_keywords'] = ""
    st.success("Input reset.")

if st.button("Start"):
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    # Google Sheets connection
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("redditData").sheet1

    # Ensure headers exist in the first row
    headers = ["Subreddit Name", "Subreddit Link", "Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"]
    existing_records = sheet.get_all_values()
    if not existing_records or existing_records[0] != headers:
        sheet.insert_row(headers, index=1)
        existing_records = sheet.get_all_values()  # Refresh data after inserting headers

    existing_links = {row[3] for row in existing_records[1:]} if len(existing_records) > 1 else set()  # Assuming permalink is in the 4th column

    # Process input
    subreddit_urls = [link.strip() for link in url_input.splitlines() if link.strip()]
    keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    keyword_urls = [f"https://www.reddit.com/r/{kw}" for kw in keywords]

    all_urls = subreddit_urls + keyword_urls

    # Generate regex patterns for contextual matching
    keyword_patterns = [re.compile(rf"\b{re.escape(kw)}(s|es|ks|ks'|es'|s'|ing|ed)?\b", re.IGNORECASE) for kw in keywords]

    all_posts_data = []

    # Handling keyword variations
    for kw in keywords:
        variations = [kw, f"{kw}s", f"{kw}es", f"{kw}ks", f"{kw}ing", f"{kw}ed"]
        for var in variations:
            url = f"https://www.reddit.com/r/{var}"
            if url not in all_urls:
                all_urls.append(url)

    for url in all_urls:
        subreddit_name = url.replace("https://www.reddit.com/r/", "").strip('/')
        try:
            subreddit = reddit.subreddit(subreddit_name)

            for post in subreddit.new(limit=None):
                matched_keywords = [kw for pattern, kw in zip(keyword_patterns, keywords) if pattern.search(post.title)]
                post_permalink = f"https://www.reddit.com{post.permalink}"

                if post_permalink not in existing_links:
                    post_info = [
                        subreddit_name,
                        url,
                        post.title,
                        post_permalink,
                        post.score,
                        datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        ", ".join(matched_keywords)
                    ]
                    all_posts_data.append(post_info)

        except Exception:
            pass

    if all_posts_data:
        sheet.append_rows(all_posts_data, value_input_option="RAW")
        st.success(f"Successfully saved {len(all_posts_data)} new posts to Google Sheets.")
    else:
        st.warning("No new posts to save.")

        

#v2
import streamlit as st
import praw
import gspread
import datetime
import re
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication using Streamlit secrets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Streamlit UI
st.title("Reddit Scraper")

# Load saved input
if 'saved_url' not in st.session_state:
    st.session_state['saved_url'] = ""
if 'saved_keywords' not in st.session_state:
    st.session_state['saved_keywords'] = ""
if 'saved_trigger_keywords' not in st.session_state:
    st.session_state['saved_trigger_keywords'] = ""

# Input fields
url_input = st.text_area("Enter subreddit links (one per line)", value=st.session_state['saved_url'])
keyword_input = st.text_area("Enter subreddit-based keywords (comma-separated)", value=st.session_state['saved_keywords'])
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=st.session_state['saved_trigger_keywords'])

# Buttons for actions
if st.button("Save Input"):
    st.session_state['saved_url'] = url_input
    st.session_state['saved_keywords'] = keyword_input
    st.session_state['saved_trigger_keywords'] = trigger_keyword_input
    st.success("Input saved.")

if st.button("Reset"):
    st.session_state['saved_url'] = ""
    st.session_state['saved_keywords'] = ""
    st.session_state['saved_trigger_keywords'] = ""
    st.success("Input reset.")

if st.button("Start"):
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    # Google Sheets connection
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("redditData").sheet1

    # Ensure headers exist in the first row
    headers = ["Subreddit Name", "Subreddit Link", "Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"]
    existing_records = sheet.get_all_values()
    if not existing_records or existing_records[0] != headers:
        sheet.insert_row(headers, index=1)
        existing_records = sheet.get_all_values()  # Refresh data after inserting headers

    existing_links = {row[3] for row in existing_records[1:]} if len(existing_records) > 1 else set()  # Assuming permalink is in the 4th column

    # Process input
    subreddit_urls = [link.strip() for link in url_input.splitlines() if link.strip()]
    subreddit_keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    trigger_keywords = [kw.strip().lower() for kw in trigger_keyword_input.split(',') if kw.strip()]

    all_urls = subreddit_urls + [f"https://www.reddit.com/r/{kw}" for kw in subreddit_keywords]

    # Generate regex patterns for trigger keywords
    trigger_patterns = [re.compile(rf"\b{re.escape(kw)}(s|es|ks|ks'|es'|s'|ing|ed)?\b", re.IGNORECASE) for kw in trigger_keywords]

    all_posts_data = []

    for url in all_urls:
        subreddit_name = url.replace("https://www.reddit.com/r/", "").strip('/')
        try:
            subreddit = reddit.subreddit(subreddit_name)

            for post in subreddit.new(limit=None):
                matched_triggers = [kw for pattern, kw in zip(trigger_patterns, trigger_keywords) if pattern.search(post.title)]
                post_permalink = f"https://www.reddit.com{post.permalink}"

                if post_permalink not in existing_links:
                    post_info = [
                        subreddit_name,
                        url,
                        post.title,
                        post_permalink,
                        post.score,
                        datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        ", ".join(matched_triggers)
                    ]
                    all_posts_data.append(post_info)

        except Exception:
            pass

    if all_posts_data:
        sheet.append_rows(all_posts_data, value_input_option="RAW")
        st.success(f"Successfully saved {len(all_posts_data)} new posts to Google Sheets.")
    else:
        st.warning("No new posts to save.")

#V2.1 WITH HEADER AND SEARCH FOR KEYWORD IN POST TITLE
import streamlit as st
import praw
import gspread
import datetime
import re
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication using Streamlit secrets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Streamlit UI
st.title("Reddit Scraper")

# Load saved input
if 'saved_url' not in st.session_state:
    st.session_state['saved_url'] = ""
if 'saved_keywords' not in st.session_state:
    st.session_state['saved_keywords'] = ""
if 'saved_trigger_keywords' not in st.session_state:
    st.session_state['saved_trigger_keywords'] = ""

# Input fields
url_input = st.text_area("Enter subreddit links (one per line)", value=st.session_state['saved_url'])
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=st.session_state['saved_keywords'])
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=st.session_state['saved_trigger_keywords'])

# Buttons for actions
if st.button("Save Input"):
    st.session_state['saved_url'] = url_input
    st.session_state['saved_keywords'] = keyword_input
    st.session_state['saved_trigger_keywords'] = trigger_keyword_input
    st.success("Input saved.")

if st.button("Reset"):
    st.session_state['saved_url'] = ""
    st.session_state['saved_keywords'] = ""
    st.session_state['saved_trigger_keywords'] = ""
    st.success("Input reset.")

if st.button("Start"):
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    # Google Sheets connection
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("redditData").sheet1

    # Ensure headers exist in the first row
    headers = ["Subreddit Name", "Subreddit Link", "Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"]
    existing_records = sheet.get_all_values()
    if not existing_records or existing_records[0] != headers:
        sheet.insert_row(headers, index=1)
        existing_records = sheet.get_all_values()  # Refresh data after inserting headers

    existing_links = {row[3] for row in existing_records[1:]} if len(existing_records) > 1 else set()  # Assuming permalink is in the 4th column

    # Process input
    subreddit_urls = [link.strip() for link in url_input.splitlines() if link.strip()]
    subreddit_keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    trigger_keywords = [kw.strip().lower() for kw in trigger_keyword_input.split(',') if kw.strip()]

    all_urls = subreddit_urls + [f"https://www.reddit.com/r/{kw}" for kw in subreddit_keywords]

    # Generate regex patterns for trigger keywords
    trigger_patterns = [re.compile(rf"\b{re.escape(kw)}(s|es|ks|ks'|es'|s'|ing|ed)?\b", re.IGNORECASE) for kw in trigger_keywords]

    all_posts_data = []

    for url in all_urls:
        subreddit_name = url.replace("https://www.reddit.com/r/", "").strip('/')
        try:
            subreddit = reddit.subreddit(subreddit_name)

            for post in subreddit.new(limit=None):
                matched_triggers = [kw for pattern, kw in zip(trigger_patterns, trigger_keywords) if pattern.search(post.title)]
                triggering_keywords = ", ".join(matched_triggers) if matched_triggers else "N/A"
                post_permalink = f"https://www.reddit.com{post.permalink}"

                if post_permalink not in existing_links:
                    post_info = [
                        subreddit_name,
                        url,
                        post.title,
                        post_permalink,
                        post.score,
                        datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        triggering_keywords
                    ]
                    all_posts_data.append(post_info)

        except Exception:
            pass

    if all_posts_data:
        sheet.append_rows(all_posts_data, value_input_option="RAW")
        st.success(f"Successfully saved {len(all_posts_data)} new posts to Google Sheets.")
    else:
        st.warning("No new posts to save.")

#with filter
import streamlit as st
import praw
import gspread
import datetime
import re
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication using Streamlit secrets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Streamlit UI
st.title("Reddit Scraper")

# Load saved input
if 'saved_url' not in st.session_state:
    st.session_state['saved_url'] = ""
if 'saved_keywords' not in st.session_state:
    st.session_state['saved_keywords'] = ""
if 'saved_trigger_keywords' not in st.session_state:
    st.session_state['saved_trigger_keywords'] = ""

# Input fields
#url_input = st.text_area("Enter subreddit links (one per line)", value=st.session_state['saved_url'])
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=st.session_state['saved_keywords'])
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=st.session_state['saved_trigger_keywords'])

# Buttons for actions
if st.button("Save Input"):
    st.session_state['saved_url'] = url_input
    st.session_state['saved_keywords'] = keyword_input
    st.session_state['saved_trigger_keywords'] = trigger_keyword_input
    st.success("Input saved.")

if st.button("Reset"):
    st.session_state['saved_url'] = ""
    st.session_state['saved_keywords'] = ""
    st.session_state['saved_trigger_keywords'] = ""
    st.success("Input reset.")

if st.button("Start"):
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    # Google Sheets connection
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("redditData").sheet1

    # Ensure headers exist in the first row
    headers = ["Subreddit Name", "Subreddit Link", "Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"]
    existing_records = sheet.get_all_values()
    if not existing_records or existing_records[0] != headers:
        sheet.insert_row(headers, index=1)
        existing_records = sheet.get_all_values()  # Refresh data after inserting headers

    existing_links = {row[3] for row in existing_records[1:]} if len(existing_records) > 1 else set()  # Assuming permalink is in the 4th column

    # Process input
    subreddit_urls = [link.strip() for link in url_input.splitlines() if link.strip()]
    subreddit_keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    trigger_keywords = [kw.strip().lower() for kw in trigger_keyword_input.split(',') if kw.strip()]

    all_urls = subreddit_urls + [f"https://www.reddit.com/r/{kw}" for kw in subreddit_keywords]

    # Generate regex patterns for trigger keywords
    trigger_patterns = [re.compile(rf"\b{re.escape(kw)}(s|es|ks|ks'|es'|s'|ing|ed)?\b", re.IGNORECASE) for kw in trigger_keywords]

    all_posts_data = []

    for url in all_urls:
        subreddit_name = url.replace("https://www.reddit.com/r/", "").strip('/')
        try:
            subreddit = reddit.subreddit(subreddit_name)

            for post in subreddit.new(limit=None):
                matched_triggers = [kw for pattern, kw in zip(trigger_patterns, trigger_keywords) if pattern.search(post.title)]
                if matched_triggers:  # Only save posts that contain a trigger keyword
                    triggering_keywords = ", ".join(matched_triggers)
                    post_permalink = f"https://www.reddit.com{post.permalink}"

                    if post_permalink not in existing_links:
                        post_info = [
                            subreddit_name,
                            url,
                            post.title,
                            post_permalink,
                            post.score,
                            datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                            triggering_keywords
                        ]
                        all_posts_data.append(post_info)
        except Exception:
            pass

    if all_posts_data:
        sheet.append_rows(all_posts_data, value_input_option="RAW")
        st.success(f"Successfully saved {len(all_posts_data)} new posts to Google Sheets.")
    else:
        st.warning("No matching posts found.")

# negativekeyword filter

import streamlit as st
import praw
import gspread
import datetime
import re
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication using Streamlit secrets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Streamlit UI
st.title("Reddit Scraper")

# Load saved input
if 'saved_keywords' not in st.session_state:
    st.session_state['saved_keywords'] = ""
if 'saved_trigger_keywords' not in st.session_state:
    st.session_state['saved_trigger_keywords'] = ""
if 'saved_negative_keywords' not in st.session_state:
    st.session_state['saved_negative_keywords'] = ""

# Input fields
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=st.session_state['saved_keywords'])
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=st.session_state['saved_trigger_keywords'])
negative_keyword_input = st.text_area("Enter negative keywords (comma-separated)", value=st.session_state['saved_negative_keywords'])

# Buttons for actions
if st.button("Save Input"):
    st.session_state['saved_keywords'] = keyword_input
    st.session_state['saved_trigger_keywords'] = trigger_keyword_input
    st.session_state['saved_negative_keywords'] = negative_keyword_input
    st.success("Input saved.")

if st.button("Reset"):
    st.session_state['saved_keywords'] = ""
    st.session_state['saved_trigger_keywords'] = ""
    st.session_state['saved_negative_keywords'] = ""
    st.success("Input reset.")

if st.button("Start"):
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    # Google Sheets connection
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("redditData").sheet1

    # Ensure headers exist in the first row
    headers = ["Subreddit Name", "Subreddit Link", "Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"]
    existing_records = sheet.get_all_values()
    if not existing_records or existing_records[0] != headers:
        sheet.insert_row(headers, index=1)
        existing_records = sheet.get_all_values()

    existing_links = {row[3] for row in existing_records[1:]} if len(existing_records) > 1 else set()

    # Process input
    subreddit_keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    trigger_keywords = [kw.strip().lower() for kw in trigger_keyword_input.split(',') if kw.strip()]
    negative_keywords = [kw.strip().lower() for kw in negative_keyword_input.split(',') if kw.strip()]

    all_urls = [f"https://www.reddit.com/r/{kw}" for kw in subreddit_keywords]

    # Generate regex patterns for keywords
    trigger_patterns = [(re.compile(rf"\b{re.escape(kw)}(s|es|ing|ed)?\b", re.IGNORECASE), kw) for kw in trigger_keywords]
    negative_patterns = [re.compile(rf"\b{re.escape(kw)}(s|es|ing|ed)?\b", re.IGNORECASE) for kw in negative_keywords]

    all_posts_data = []

    for url in all_urls:
        subreddit_name = url.replace("https://www.reddit.com/r/", "").strip('/')
        try:
            subreddit = reddit.subreddit(subreddit_name)

            for post in subreddit.new(limit=None):
                matched_triggers = [kw for pattern, kw in trigger_patterns if pattern.search(post.title)]
                contains_negative = any(pattern.search(post.title) for pattern in negative_patterns)
                
                # Only save posts that contain a trigger keyword and do not contain a negative keyword
                if matched_triggers and not contains_negative:
                    triggering_keywords = ", ".join(matched_triggers)
                    post_permalink = f"https://www.reddit.com{post.permalink}"

                    if post_permalink not in existing_links:
                        post_info = [
                            subreddit_name,
                            url,
                            post.title,
                            post_permalink,
                            post.score,
                            datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                            triggering_keywords
                        ]
                        all_posts_data.append(post_info)
        except Exception:
            pass

    if all_posts_data:
        sheet.append_rows(all_posts_data, value_input_option="RAW")
        st.success(f"Successfully saved {len(all_posts_data)} new posts to Google Sheets.")
    else:
        st.warning("No matching posts found.")

    
#with folder structure 
import streamlit as st
import praw
import gspread
import datetime
import re
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication using Streamlit secrets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Initialize session state for folders
if "folders" not in st.session_state:
    st.session_state["folders"] = {}
if "current_folder" not in st.session_state:
    st.session_state["current_folder"] = ""

# Sidebar for folders
st.sidebar.header("Folders")
for folder_name in st.session_state["folders"]:
    if st.sidebar.button(folder_name):
        st.session_state["current_folder"] = folder_name

# Main UI
st.title("Reddit Scraper")

# Load saved input if a folder is selected
selected_folder = st.session_state["current_folder"]
if selected_folder:
    saved_data = st.session_state["folders"].get(selected_folder, {})
else:
    saved_data = {}

# Input fields
#url_input = st.text_area("Enter subreddit links (one per line)", value=saved_data.get("urls", ""))
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=saved_data.get("keywords", ""))
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=saved_data.get("trigger_keywords", ""))
negative_keyword_input = st.text_area("Enter negative keywords (comma-separated)", value=saved_data.get("negative_keywords", ""))

# Save input as a new folder
if st.button("Save Input"):
    folder_name = f"Scrape {len(st.session_state['folders']) + 1}"
    st.session_state["folders"][folder_name] = {
        "urls": url_input,
        "keywords": keyword_input,
        "trigger_keywords": trigger_keyword_input,
        "negative_keywords": negative_keyword_input
    }
    st.session_state["current_folder"] = folder_name
    st.success(f"Saved as {folder_name}")

# Reset input fields
if st.button("Reset"):
    st.session_state["current_folder"] = ""
    st.success("Input reset.")

# Start processing
if st.button("Start") and selected_folder:
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("redditData").sheet1

    headers = ["Subreddit Name", "Subreddit Link", "Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"]
    existing_records = sheet.get_all_values()
    if not existing_records or existing_records[0] != headers:
        sheet.insert_row(headers, index=1)

    subreddit_keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    trigger_keywords = [kw.strip().lower() for kw in trigger_keyword_input.split(',') if kw.strip()]
    negative_keywords = [kw.strip().lower() for kw in negative_keyword_input.split(',') if kw.strip()]
    trigger_patterns = [re.compile(rf"\b{re.escape(kw)}(s|es|ing|ed)?\b", re.IGNORECASE) for kw in trigger_keywords]
    negative_patterns = [re.compile(rf"\b{re.escape(kw)}(s|es|ing|ed)?\b", re.IGNORECASE) for kw in negative_keywords]

    all_posts_data = []
    for subreddit_name in subreddit_keywords:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for post in subreddit.new(limit=None):
                matched_triggers = [kw for pattern, kw in zip(trigger_patterns, trigger_keywords) if pattern.search(post.title)]
                matched_negatives = [kw for pattern, kw in zip(negative_patterns, negative_keywords) if pattern.search(post.title)]
                if matched_triggers and not matched_negatives:
                    all_posts_data.append([
                        subreddit_name,
                        f"https://www.reddit.com/r/{subreddit_name}",
                        post.title,
                        f"https://www.reddit.com{post.permalink}",
                        post.score,
                        datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        ", ".join(matched_triggers)
                    ])
        except Exception:
            pass

    if all_posts_data:
        sheet.append_rows(all_posts_data, value_input_option="RAW")
        st.success(f"Saved {len(all_posts_data)} new posts.")
    else:
        st.warning("No matching posts found.")


#final with out folder
import streamlit as st
import praw
import gspread
import datetime
import re
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Streamlit UI
st.title("Reddit Scraper")

# Load saved input
if 'saved_keywords' not in st.session_state:
    st.session_state['saved_keywords'] = ""
if 'saved_trigger_keywords' not in st.session_state:
    st.session_state['saved_trigger_keywords'] = ""
if 'saved_negative_keywords' not in st.session_state:
    st.session_state['saved_negative_keywords'] = ""

# Input fields
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=st.session_state['saved_keywords'])
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=st.session_state['saved_trigger_keywords'])
negative_keyword_input = st.text_area("Enter negative keywords (comma-separated)", value=st.session_state['saved_negative_keywords'])

# Buttons for actions
if st.button("Save Input"):
    st.session_state['saved_keywords'] = keyword_input
    st.session_state['saved_trigger_keywords'] = trigger_keyword_input
    st.session_state['saved_negative_keywords'] = negative_keyword_input
    st.success("Input saved.")

if st.button("Reset"):
    st.session_state['saved_keywords'] = ""
    st.session_state['saved_trigger_keywords'] = ""
    st.session_state['saved_negative_keywords'] = ""
    st.success("Input reset.")

if st.button("Start"):
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    # Google Sheets connection
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open("redditData")  # Main Google Sheet

    # Process input
    subreddit_keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    trigger_keywords = [kw.strip().lower() for kw in trigger_keyword_input.split(',') if kw.strip()]
    negative_keywords = [kw.strip().lower() for kw in negative_keyword_input.split(',') if kw.strip()]

    # Generate regex patterns for trigger and negative keywords
    trigger_patterns = [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in trigger_keywords]
    negative_patterns = [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in negative_keywords]

    for subreddit_name in subreddit_keywords:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            sheet_name = subreddit_name.capitalize()

            # Check if a sheet exists for this subreddit, if not create one
            try:
                sheet = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="7")
                sheet.append_row(["Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"])

            existing_records = sheet.get_all_values()
            existing_links = {row[1] for row in existing_records[1:]} if len(existing_records) > 1 else set()

            all_posts_data = []

            for post in subreddit.new(limit=None):
                post_title = post.title.lower()
                post_permalink = f"https://www.reddit.com{post.permalink}"

                # Check if post contains trigger keywords and does NOT contain negative keywords
                matched_triggers = [kw for pattern, kw in zip(trigger_patterns, trigger_keywords) if pattern.search(post_title)]
                matched_negatives = any(pattern.search(post_title) for pattern in negative_patterns)

                if matched_triggers and not matched_negatives and post_permalink not in existing_links:
                    triggering_keywords = ", ".join(matched_triggers)
                    post_info = [
                        post.title,
                        post_permalink,
                        post.score,
                        datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        triggering_keywords
                    ]
                    all_posts_data.append(post_info)

            # Save data to the respective sheet
            if all_posts_data:
                sheet.append_rows(all_posts_data, value_input_option="RAW")
                st.success(f"Successfully saved {len(all_posts_data)} new posts to {sheet_name}.")
            else:
                st.warning(f"No matching posts found for {sheet_name}.")
        
        except Exception as e:
            st.error(f"Error fetching subreddit {subreddit_name}: {e}")
            

#final with folder and separate sheets
import streamlit as st
import praw
import gspread
import datetime
import re
import os
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Define folder path for saving setups
FOLDER_PATH = "saved_scrapes"
os.makedirs(FOLDER_PATH, exist_ok=True)

# Streamlit UI
st.title("Reddit Scraper")

# Load saved input
if 'saved_keywords' not in st.session_state:
    st.session_state['saved_keywords'] = ""
if 'saved_trigger_keywords' not in st.session_state:
    st.session_state['saved_trigger_keywords'] = ""
if 'saved_negative_keywords' not in st.session_state:
    st.session_state['saved_negative_keywords'] = ""

# Input fields
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=st.session_state['saved_keywords'])
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=st.session_state['saved_trigger_keywords'])
negative_keyword_input = st.text_area("Enter negative keywords (comma-separated)", value=st.session_state['saved_negative_keywords'])

# Load existing folders
existing_folders = sorted(os.listdir(FOLDER_PATH))
st.sidebar.header("Folders")
for folder in existing_folders:
    if st.sidebar.button(folder):
        folder_path = os.path.join(FOLDER_PATH, folder)
        with open(os.path.join(folder_path, "keywords.txt"), "r") as f:
            st.session_state['saved_keywords'] = f.read()
        with open(os.path.join(folder_path, "trigger_keywords.txt"), "r") as f:
            st.session_state['saved_trigger_keywords'] = f.read()
        with open(os.path.join(folder_path, "negative_keywords.txt"), "r") as f:
            st.session_state['saved_negative_keywords'] = f.read()
        st.experimental_rerun()

# Buttons for actions
if st.button("Save Input"):
    folder_name = f"Scrape_{len(existing_folders) + 1}"
    folder_path = os.path.join(FOLDER_PATH, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, "keywords.txt"), "w") as f:
        f.write(keyword_input)
    with open(os.path.join(folder_path, "trigger_keywords.txt"), "w") as f:
        f.write(trigger_keyword_input)
    with open(os.path.join(folder_path, "negative_keywords.txt"), "w") as f:
        f.write(negative_keyword_input)
    st.success(f"Setup saved as {folder_name}")
    st.experimental_rerun()

if st.button("Reset"):
    st.session_state['saved_keywords'] = ""
    st.session_state['saved_trigger_keywords'] = ""
    st.session_state['saved_negative_keywords'] = ""
    st.success("Input reset.")
    st.experimental_rerun()

if st.button("Start"):
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    # Google Sheets connection
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open("redditData")  # Main Google Sheet

    # Process input
    subreddit_keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    trigger_keywords = [kw.strip().lower() for kw in trigger_keyword_input.split(',') if kw.strip()]
    negative_keywords = [kw.strip().lower() for kw in negative_keyword_input.split(',') if kw.strip()]

    # Generate regex patterns for trigger and negative keywords
    trigger_patterns = [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in trigger_keywords]
    negative_patterns = [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in negative_keywords]

    for subreddit_name in subreddit_keywords:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            sheet_name = subreddit_name.capitalize()

            # Check if a sheet exists for this subreddit, if not create one
            try:
                sheet = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="7")
                sheet.append_row(["Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"])

            existing_records = sheet.get_all_values()
            existing_links = {row[1] for row in existing_records[1:]} if len(existing_records) > 1 else set()

            all_posts_data = []

            for post in subreddit.new(limit=None):
                post_title = post.title.lower()
                post_permalink = f"https://www.reddit.com{post.permalink}"

                # Check if post contains trigger keywords and does NOT contain negative keywords
                matched_triggers = [kw for pattern, kw in zip(trigger_patterns, trigger_keywords) if pattern.search(post_title)]
                matched_negatives = any(pattern.search(post_title) for pattern in negative_patterns)

                if matched_triggers and not matched_negatives and post_permalink not in existing_links:
                    triggering_keywords = ", ".join(matched_triggers)
                    post_info = [
                        post.title,
                        post_permalink,
                        post.score,
                        datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        triggering_keywords
                    ]
                    all_posts_data.append(post_info)

            # Save data to the respective sheet
            if all_posts_data:
                sheet.append_rows(all_posts_data, value_input_option="RAW")
                st.success(f"Successfully saved {len(all_posts_data)} new posts to {sheet_name}.")
            else:
                st.warning(f"No matching posts found for {sheet_name}.")

        except Exception as e:
            st.error(f"Error fetching subreddit {subreddit_name}: {e}")
'''
import streamlit as st
import praw
import gspread
import datetime
import re
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Initialize session state for folders
if "folders" not in st.session_state:
    st.session_state["folders"] = {}
if "current_folder" not in st.session_state:
    st.session_state["current_folder"] = ""

# Sidebar for folder selection
st.sidebar.header("Folders")
for folder_name in st.session_state["folders"]:
    if st.sidebar.button(folder_name):
        st.session_state["current_folder"] = folder_name

# Main UI
st.title("Reddit Scraper")

# Load saved input if a folder is selected
selected_folder = st.session_state["current_folder"]
saved_data = st.session_state["folders"].get(selected_folder, {}) if selected_folder else {}

# Input fields
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=saved_data.get("keywords", ""))
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=saved_data.get("trigger_keywords", ""))
negative_keyword_input = st.text_area("Enter negative keywords (comma-separated)", value=saved_data.get("negative_keywords", ""))

# Save input as a new folder
if st.button("Save Input"):
    folder_name = f"Scrape {len(st.session_state['folders']) + 1}"
    st.session_state["folders"][folder_name] = {
        "keywords": keyword_input,
        "trigger_keywords": trigger_keyword_input,
        "negative_keywords": negative_keyword_input
    }
    st.session_state["current_folder"] = folder_name
    st.success(f"Saved as {folder_name}")

# Reset input fields
if st.button("Reset"):
    st.session_state["current_folder"] = ""
    st.success("Input reset.")

# Start processing
if st.button("Start") and selected_folder:
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds_file"], SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open("redditData")

    subreddit_keywords = [kw.strip().lower() for kw in keyword_input.split(',') if kw.strip()]
    trigger_keywords = [kw.strip().lower() for kw in trigger_keyword_input.split(',') if kw.strip()]
    negative_keywords = [kw.strip().lower() for kw in negative_keyword_input.split(',') if kw.strip()]

    trigger_patterns = [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in trigger_keywords]
    negative_patterns = [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in negative_keywords]

    for subreddit_name in subreddit_keywords:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            sheet_name = subreddit_name.capitalize()

            try:
                sheet = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="7")
                sheet.append_row(["Post Title", "Post Link", "Post Upvotes", "Post Date", "Triggering Keywords"])

            existing_records = sheet.get_all_values()
            existing_links = {row[1] for row in existing_records[1:]} if len(existing_records) > 1 else set()
            all_posts_data = []

            for post in subreddit.new(limit=None):
                post_title = post.title.lower()
                post_permalink = f"https://www.reddit.com{post.permalink}"

                matched_triggers = [kw for pattern, kw in zip(trigger_patterns, trigger_keywords) if pattern.search(post_title)]
                matched_negatives = any(pattern.search(post_title) for pattern in negative_patterns)

                if matched_triggers and not matched_negatives and post_permalink not in existing_links:
                    all_posts_data.append([
                        post.title,
                        post_permalink,
                        post.score,
                        datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        ", ".join(matched_triggers)
                    ])

            if all_posts_data:
                sheet.append_rows(all_posts_data, value_input_option="RAW")
                st.success(f"Successfully saved {len(all_posts_data)} new posts to {sheet_name}.")
            else:
                st.warning(f"No matching posts found for {sheet_name}.")

        except Exception as e:
            st.error(f"Error fetching subreddit {subreddit_name}: {e}")
