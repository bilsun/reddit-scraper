# EXPORTS CSV FILE WITH ALL COMMENTS FROM SPECIFIED REDDIT POST(S)
# outputs to data > scraped_comments

from psaw import PushshiftAPI
import pandas as pd
import datetime as dt
import time
import re 

start_time = time.time()

# [INPUT NEEDED] -------------------------------
# replace these variables according to your Reddit scraping needs:

# if scraping comments from specific post(s)
post_ids = '8ejcor' # 6-character post ids can be scraped or found in a post's URL: https://www.reddit.com/r/pushshift/comments/8ejcor/how_can_i_get_all_comments_or_at_least_the/

# specify file name for exported csv (change between runs to prevent overwriting existing data)
exported_file_name = 'scraped_reddit_comments'

# -----------------------------------------------

# function that formats text for readability 

def clean_text(text):
    text = text.strip()
    text = re.sub('\n+', '\n', text)
    text = re.sub('&amp;', '&', text)
    text = re.sub('&lt;', '<', text)
    text = re.sub('&gt;', '>', text)
    text = re.sub('&#x200B;', '', text)
    text = re.sub('&nbsp;', ' ', text)
    return text

# -----------------------------------------------

print("collecting Reddit data...")

api = PushshiftAPI()
gen = api.search_comments(link_id=post_ids) 
comments = list(gen)
df = pd.DataFrame([thing.d_ for thing in comments])

print("successful data collection!\n")

# -----------------------------------------------

print("cleaning and formatting data...\n")

df['body'] = df['body'].apply(lambda x: clean_text(x))
df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
df['date'] = df['created_utc'].apply(lambda x: pd.Timestamp.to_pydatetime(x))
df['link'] = 'https://www.reddit.com' + df['permalink']

# -----------------------------------------------

df_simplified = df[['author','body','date','is_submitter','link','subreddit']] # comment scores should be updated with PRAW for accuracy (otherwise exclude from analysis)
df_simplified.to_csv(f'./data/scraped_comments/{exported_file_name}.csv', index=False, header=True)

# -----------------------------------------------

runtime = '{:.0f}'.format(time.time() - start_time)
print(f"--- DONE! runtime: {runtime} seconds ---")
print("see data > scraped_comments for exported csv file \n")