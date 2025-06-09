from google_play_scraper import Sort, reviews
import csv
from datetime import datetime
import schedule
import logging
import time

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_play_store_reviews():
    APP_ID = 'com.dashen.dashensuperapp'
    logging.info("🔄 Fetching reviews...")

    try:
        results, _ = reviews( # Fetch reviews from the Google Play Store, _ is used to ignore the second return value which contains pagination info and result is the list of reviews
            APP_ID,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=5000,
            filter_score_with=None
        )
        logging.info(f"✅ Fetched {len(results)} reviews") # Log the number of reviews fetched
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') # Format the current timestamp for the filename
        # Create a filename with the current timestamp
        filename = f'Dashen_reviews_{timestamp}.csv'

        # Write to CSV without using pandas
        with open(filename, mode='w', newline='', encoding='utf-8') as file: # Open the file in write mode with UTF-8 encoding
            # Define the fieldnames for the CSV
            writer = csv.DictWriter(file, fieldnames=['review_text', 'rating', 'date', 'bank_name', 'source'])
            writer.writeheader()

            for entry in results: # Iterate over the list of reviews
                writer.writerow({ # Write each review to the CSV file
                    'review_text': entry['content'],
                    'rating': entry['score'],
                    'date': entry['at'].strftime('%Y-%m-%d'),
                    'bank_name': 'Dashe Bank Super App',
                    'source': 'Google Play'
                })

        logging.info(f"✅ Saved {len(results)} reviews to {filename}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")

# Different scheduling options (uncomment the one you want to use):
# schedule.every().day.at("07:00").do(scrape_play_store_reviews)  # Daily at 1 AM
# schedule.every(6).hours.do(scrape_play_store_reviews)           # Every 6 hours
# schedule.every().monday.do(scrape_play_store_reviews)           # Every Monday
# schedule.every().hour.do(scrape_play_store_reviews)             # Every hour

schedule.every(1).minutes.do(scrape_play_store_reviews) # Every minute for testing

while True:
    schedule.run_pending()
    time.sleep(1)


# from google_play_scraper import Sort, reviews
# import csv
# from datetime import datetime
# import schedule
# import logging
# import time
# import os

# # Ensure 'data' directory exists
# os.makedirs('data', exist_ok=True) #exists_ok=True ensures that the directory is created if it doesn't already exist

# # Set up logging
# logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Log format includes timestamp, log level, and message
# #level=logging.INFO means that all messages at this level and above will be logged (INFO, WARNING, ERROR, CRITICAL)
# # App configuration
# APPS = {
#     'CBE': {
#         'app_id': 'com.combanketh.mobilebanking',
#         'bank_name': 'Commercial Bank of Ethiopia',
#     },
#     'BOA': {
#         'app_id': 'com.boa.boaMobileBanking',
#         'bank_name': 'Bank of Abyssinia',
#     },
#     'Dashen': {
#         'app_id': 'com.dashen.dashensuperapp',
#         'bank_name': 'Dashen Bank Super App',
#     }
# }

# def scrape_reviews_for_app(app_code, app_info):
#     app_id = app_info['app_id']
#     bank_name = app_info['bank_name']
#     logging.info(f" Fetching reviews for {bank_name}...")

#     try:
#         results, _ = reviews( # Fetch reviews from the Google Play Store, _ is used to ignore the second return value which contains pagination info and result is the list of reviews
#             app_id,
#             lang='en',
#             country='us',
#             sort=Sort.NEWEST, # Sort reviews by newest first
#             count=5000,
#             filter_score_with=None
#         )
#         print("Results:", results)  # Add this line to check if results is empty

#         logging.info(f"✅ Fetched {len(results)} reviews for {bank_name}")

#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') # Format the current timestamp for the filename, strftime('%Y%m%d_%H%M%S') formats the date and time into a string
#         # Create a filename with the current timestamp
#         filename = os.path.join('data', f'{app_code}_reviews_{timestamp}.csv')

#         with open(filename, mode='w', newline='', encoding='utf-8') as file: # Open the file in write mode with UTF-8 encoding, mode='w' means the file is opened for writing, and if it already exists, it will be overwritten
#             # Write to CSV without using pandas
#             writer = csv.DictWriter(file, fieldnames=['review_text', 'rating', 'date', 'bank_name', 'source'])
#             writer.writeheader() # Write the fieldnames to the file

#             for entry in results:
#                 writer.writerow({ # Write each review to the CSV file
#                     'review_text': entry['content'],
#                     'rating': entry['score'],
#                     'date': entry['at'].strftime('%Y-%m-%d'), # Convert the date to a string in 'YYYY-MM-DD' format
#                     'bank_name': bank_name,
#                     'source': 'Google Play'
#                 })

#         logging.info(f"✅ Saved {len(results)} reviews for {bank_name} to {filename}")
#     except Exception as e:
#         logging.error(f" Error fetching reviews for {bank_name}: {e}")

# def scrape_all_apps():
#     for app_code, app_info in APPS.items():
#         scrape_reviews_for_app(app_code, app_info)
#         print(f"Scraped reviews for {app_info['bank_name']} ({app_code})")

# # Schedule (currently set for every minute for testing)
# schedule.every(1).minutes.do(scrape_all_apps)

# # Main loop
# while True:
#     schedule.run_pending()
#     time.sleep(1)
