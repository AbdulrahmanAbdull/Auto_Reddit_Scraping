'''
import streamlit as st
import praw
import gspread
import datetime
import re
import json
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Load saved folder data from session state or file
if "folders" not in st.session_state:
    try:
        with open("folders.json", "r") as f:
            st.session_state["folders"] = json.load(f)
    except FileNotFoundError:
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

# Save or update input for the selected folder
if st.button("Save Input"):
    if selected_folder:
        st.session_state["folders"][selected_folder] = {
            "keywords": keyword_input,
            "trigger_keywords": trigger_keyword_input,
            "negative_keywords": negative_keyword_input
        }
        st.success(f"Updated {selected_folder}")
    else:
        folder_name = f"Scrape {len(st.session_state['folders']) + 1}"
        st.session_state["folders"][folder_name] = {
            "keywords": keyword_input,
            "trigger_keywords": trigger_keyword_input,
            "negative_keywords": negative_keyword_input
        }
        st.session_state["current_folder"] = folder_name
        st.success(f"Saved as {folder_name}")
    with open("folders.json", "w") as f:
        json.dump(st.session_state["folders"], f)

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

#v2
import streamlit as st
import praw
import gspread
import datetime
import re
import json
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Load saved folder data from session state or file
if "folders" not in st.session_state:
    try:
        with open("folders.json", "r") as f:
            st.session_state["folders"] = json.load(f)
    except FileNotFoundError:
        st.session_state["folders"] = {}

if "current_folder" not in st.session_state:
    st.session_state["current_folder"] = ""

# Sidebar for folder selection
st.sidebar.header("Folders")
for folder_name in list(st.session_state["folders"].keys()):
    col1, col2, col3 = st.sidebar.columns([5, 1, 1])
    with col1:
        if st.button(folder_name, key=f"folder_{folder_name}"):
            st.session_state["current_folder"] = folder_name
    with col2:
        if st.button("✏️", key=f"edit_{folder_name}"):
            new_name = st.text_input("Rename folder:", value=folder_name, key=f"rename_{folder_name}")
            if st.button("Save Rename", key=f"save_rename_{folder_name}"):
                st.session_state["folders"][new_name] = st.session_state["folders"].pop(folder_name)
                st.session_state["current_folder"] = new_name
                with open("folders.json", "w") as f:
                    json.dump(st.session_state["folders"], f)
                st.experimental_rerun()
    with col3:
        if st.button("🗑️", key=f"delete_{folder_name}"):
            del st.session_state["folders"][folder_name]
            st.session_state["current_folder"] = ""
            with open("folders.json", "w") as f:
                json.dump(st.session_state["folders"], f)
            st.experimental_rerun()

# Main UI
st.title("Reddit Scraper")

# Load saved input if a folder is selected
selected_folder = st.session_state["current_folder"]
saved_data = st.session_state["folders"].get(selected_folder, {}) if selected_folder else {}

# Input fields
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=saved_data.get("keywords", ""))
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=saved_data.get("trigger_keywords", ""))
negative_keyword_input = st.text_area("Enter negative keywords (comma-separated)", value=saved_data.get("negative_keywords", ""))

# Save or update input for the selected folder
if st.button("Save Input"):
    if selected_folder:
        st.session_state["folders"][selected_folder] = {
            "keywords": keyword_input,
            "trigger_keywords": trigger_keyword_input,
            "negative_keywords": negative_keyword_input
        }
        st.success(f"Updated {selected_folder}")
    else:
        st.warning("Please select a folder to update.")
    with open("folders.json", "w") as f:
        json.dump(st.session_state["folders"], f)

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

#v3
import streamlit as st
import praw
import gspread
import datetime
import re
import json
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Load saved folder data from session state or file
if "folders" not in st.session_state:
    try:
        with open("folders.json", "r") as f:
            st.session_state["folders"] = json.load(f)
    except FileNotFoundError:
        st.session_state["folders"] = {}

if "current_folder" not in st.session_state:
    st.session_state["current_folder"] = ""

# Sidebar for folder selection
st.sidebar.header("Folders")
for folder_name in list(st.session_state["folders"].keys()):
    col1, col2, col3 = st.sidebar.columns([5, 1, 1])
    with col1:
        if st.button(folder_name, key=f"folder_{folder_name}"):
            st.session_state["current_folder"] = folder_name
    with col2:
        if st.button("✏️", key=f"edit_{folder_name}"):
            new_name = st.text_input("Rename folder:", value=folder_name, key=f"rename_{folder_name}")
            if st.button("Save Rename", key=f"save_rename_{folder_name}"):
                st.session_state["folders"][new_name] = st.session_state["folders"].pop(folder_name)
                st.session_state["current_folder"] = new_name
                with open("folders.json", "w") as f:
                    json.dump(st.session_state["folders"], f)
                st.experimental_rerun()
    with col3:
        if st.button("🗑️", key=f"delete_{folder_name}"):
            del st.session_state["folders"][folder_name]
            st.session_state["current_folder"] = ""
            with open("folders.json", "w") as f:
                json.dump(st.session_state["folders"], f)
            try:
                st.experimental_rerun()
            except AttributeError:
                pass

# Main UI
st.title("Reddit Scraper")

# Load saved input if a folder is selected
selected_folder = st.session_state["current_folder"]
saved_data = st.session_state["folders"].get(selected_folder, {}) if selected_folder else {}

# Input fields
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=saved_data.get("keywords", ""))
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=saved_data.get("trigger_keywords", ""))
negative_keyword_input = st.text_area("Enter negative keywords (comma-separated)", value=saved_data.get("negative_keywords", ""))

# Save or update input for the selected folder
if st.button("Save Input"):
    if selected_folder:
        st.session_state["folders"][selected_folder] = {
            "keywords": keyword_input,
            "trigger_keywords": trigger_keyword_input,
            "negative_keywords": negative_keyword_input
        }
        st.success(f"Updated {selected_folder}")
    else:
        st.warning("Please select a folder to update.")
    with open("folders.json", "w") as f:
        json.dump(st.session_state["folders"], f)

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
'''
import streamlit as st
import praw
import gspread
import datetime
import re
import json
from oauth2client.service_account import ServiceAccountCredentials

# Reddit API credentials
REDDIT_CLIENT_ID = "lWFWfRPV8_EHqjRpAdzclA"
REDDIT_CLIENT_SECRET = "TUfF3yHH80wYOSCvtXajFQ9QkblXmQ"
REDDIT_USER_AGENT = "scraping"

# Google Sheets authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = st.secrets["google_creds_file"]

# Load saved folder data from session state or file
if "folders" not in st.session_state:
    try:
        with open("folders.json", "r") as f:
            st.session_state["folders"] = json.load(f)
    except FileNotFoundError:
        st.session_state["folders"] = {}

if "current_folder" not in st.session_state:
    st.session_state["current_folder"] = ""

# Sidebar for folder selection
st.sidebar.header("Folders")
for folder_name in list(st.session_state["folders"].keys()):
    col1, col2 = st.sidebar.columns([5, 1])
    with col1:
        if st.button(folder_name, key=f"folder_{folder_name}"):
            st.session_state["current_folder"] = folder_name
    with col2:
        if st.button("🗑️", key=f"delete_{folder_name}"):
            del st.session_state["folders"][folder_name]
            st.session_state["current_folder"] = ""
            with open("folders.json", "w") as f:
                json.dump(st.session_state["folders"], f)
            try:
                st.experimental_rerun()
            except AttributeError:
                pass

# Main UI
st.title("Reddit Scraper")

# Load saved input if a folder is selected
selected_folder = st.session_state["current_folder"]
saved_data = st.session_state["folders"].get(selected_folder, {}) if selected_folder else {}

# Input fields
keyword_input = st.text_area("Enter subreddit-name (comma-separated)", value=saved_data.get("keywords", ""))
trigger_keyword_input = st.text_area("Enter keywords triggered in post titles (comma-separated)", value=saved_data.get("trigger_keywords", ""))
negative_keyword_input = st.text_area("Enter negative keywords (comma-separated)", value=saved_data.get("negative_keywords", ""))

# Save or update input for the selected folder
if st.button("Save Input"):
    if selected_folder:
        st.session_state["folders"][selected_folder] = {
            "keywords": keyword_input,
            "trigger_keywords": trigger_keyword_input,
            "negative_keywords": negative_keyword_input
        }
        st.success(f"Updated {selected_folder}")
    else:
        st.warning("Please select a folder to update.")
    with open("folders.json", "w") as f:
        json.dump(st.session_state["folders"], f)

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
