# main_aggregation_script.py
import pandas as pd
from sentiment_analysis_service import SentimentService # Assuming this is in your project root

def aggregate_sentiments(data_with_sentiments, sentiment_score_key, group_by_columns):
    """
    Aggregates sentiment scores.

    Args:
        data_with_sentiments (list of dict): List of dictionaries, each containing
                                             the sentiment score and grouping keys.
        sentiment_score_key (str): The key in the dictionaries that holds the
                                   numerical sentiment score to be averaged.
        group_by_columns (list of str): List of column names to group by (e.g., ['bank', 'rating']).

    Returns:
        pandas.DataFrame: DataFrame with aggregated mean sentiment scores.
    """
    if not data_with_sentiments:
        print("No data to aggregate.")
        return pd.DataFrame()

    df = pd.DataFrame(data_with_sentiments)

    if sentiment_score_key not in df.columns:
        raise ValueError(f"Sentiment score key '{sentiment_score_key}' not found in the data.")
    for col in group_by_columns:
        if col not in df.columns:
            raise ValueError(f"Grouping column '{col}' not found in the data.")

    # Ensure the sentiment score is numeric
    df[sentiment_score_key] = pd.to_numeric(df[sentiment_score_key], errors='coerce')
    
    # Drop rows where sentiment score could not be converted to numeric (if any)
    df.dropna(subset=[sentiment_score_key], inplace=True)

    if df.empty:
        print("No valid numeric sentiment scores found after cleaning.")
        return pd.DataFrame()
        
    aggregated_data = df.groupby(group_by_columns)[sentiment_score_key].mean().reset_index()
    aggregated_data.rename(columns={sentiment_score_key: f'mean_{sentiment_score_key}'}, inplace=True)
    
    return aggregated_data

if __name__ == "__main__":
    # 1. Sample Input Data (text, bank, rating)
    sample_data = [
        {"id": 1, "review_text": "Great service from Bank Alpha!", "bank": "Bank Alpha", "rating": 5},
        {"id": 2, "review_text": "Bank Alpha was okay, not special.", "bank": "Bank Alpha", "rating": 3},
        {"id": 3, "review_text": "Terrible experience with Beta Bank.", "bank": "Beta Bank", "rating": 1},
        {"id": 4, "review_text": "Bank Alpha lost my money, awful!", "bank": "Bank Alpha", "rating": 1},
        {"id": 5, "review_text": "Beta Bank resolved my issue quickly and was very positive.", "bank": "Beta Bank", "rating": 4},
        {"id": 6, "review_text": "I love Gamma Bank, best rates.", "bank": "Gamma Bank", "rating": 5},
        {"id": 7, "review_text": "Gamma Bank customer support is slow and unhelpful.", "bank": "Gamma Bank", "rating": 2},
        {"id": 8, "review_text": "Bank Alpha is consistently bad for 1-star issues.", "bank": "Bank Alpha", "rating": 1},
        {"id": 9, "review_text": "Beta Bank is just average.", "bank": "Beta Bank", "rating": 3},
        {"id": 10, "review_text": "This is a neutral statement about nothing in particular.", "bank": "Bank Alpha", "rating": 3} # Neutral text
    ]

    # 2. Initialize SentimentService
    # Using VADER for this example as its 'compound' score is a good single metric for averaging.
    # You can change to 'distilbert' or 'textblob' if preferred.
    sentiment_model_to_use = 'vader' # or 'textblob', or 'distilbert'
    service = SentimentService(default_model=sentiment_model_to_use)

    # 3. Calculate Sentiment Scores and Combine Data
    data_with_sentiments = []
    print(f"Calculating sentiments using {sentiment_model_to_use}...\n")
    for item in sample_data:
        text_to_analyze = item["review_text"]
        analysis_result = service.analyze(text_to_analyze, model_type=sentiment_model_to_use)
        
        # Prepare a dictionary to store with original data
        processed_item = item.copy() # Start with original data

        if sentiment_model_to_use == 'vader':
            # VADER's compound score is good for averaging (-1 to 1)
            processed_item['sentiment_score'] = analysis_result['scores']['compound']
            processed_item['sentiment_label'] = analysis_result['label']
        elif sentiment_model_to_use == 'textblob':
            # TextBlob's polarity score is good for averaging (-1 to 1)
            processed_item['sentiment_score'] = analysis_result['scores']['polarity']
            processed_item['sentiment_label'] = analysis_result['label']
        elif sentiment_model_to_use == 'distilbert':
            # For DistilBERT, we can create a composite score (e.g., POSITIVE - NEGATIVE)
            # or average one of the scores directly (e.g., POSITIVE score).
            # Here, let's use POSITIVE - NEGATIVE, which ranges from -1 to 1.
            positive_score = analysis_result['scores'].get('POSITIVE', 0.0)
            negative_score = analysis_result['scores'].get('NEGATIVE', 0.0)
            processed_item['sentiment_score'] = positive_score - negative_score
            processed_item['sentiment_label'] = analysis_result['label'] # POSITIVE, NEGATIVE, or inferred NEUTRAL
            # You could also store individual scores:
            # processed_item['positive_score'] = positive_score
            # processed_item['negative_score'] = negative_score
        else:
            print(f"Warning: Score extraction not defined for model {sentiment_model_to_use}")
            processed_item['sentiment_score'] = None # Or handle as an error

        data_with_sentiments.append(processed_item)
        print(f"Text: \"{text_to_analyze}\"")
        print(f"  Bank: {item['bank_name']}, Rating: {item['rating']}")
        print(f"  Sentiment Score ({sentiment_model_to_use}): {processed_item.get('sentiment_score', 'N/A')}, Label: {processed_item.get('sentiment_label', 'N/A')}")
        print("-" * 30)

    # 4. Aggregate
    print("\n--- Aggregating Sentiments ---")

    # Example 1: Mean sentiment per bank and rating
    print("\nMean sentiment score by Bank and Rating:")
    agg_by_bank_rating = aggregate_sentiments(
        data_with_sentiments,
        sentiment_score_key='sentiment_score',
        group_by_columns=['bank_name', 'rating']
    )
    print(agg_by_bank_rating.to_string())

    # Example 2: Mean sentiment per rating (across all banks)
    # This directly addresses "mean sentiment for 1-star rating"
    print("\nMean sentiment score by Rating (across all banks):")
    agg_by_rating = aggregate_sentiments(
        data_with_sentiments,
        sentiment_score_key='sentiment_score',
        group_by_columns=['rating']
    )
    print(agg_by_rating.to_string())

    # Example 3: Mean sentiment per bank (across all ratings)
    print("\nMean sentiment score by Bank (across all ratings):")
    agg_by_bank = aggregate_sentiments(
        data_with_sentiments,
        sentiment_score_key='sentiment_score',
        group_by_columns=['bank_name']
    )
    print(agg_by_bank.to_string())

    # If you used DistilBERT and stored 'positive_score' and 'negative_score' separately,
    # you could aggregate them individually too:
    # if sentiment_model_to_use == 'distilbert':
    #     print("\nMean POSITIVE score (DistilBERT) by Bank and Rating:")
    #     # First, ensure 'positive_score' was added to data_with_sentiments
    #     # For this to work, you'd need to modify the loop above to add 'positive_score'
    #     # e.g., processed_item['positive_score'] = analysis_result['scores'].get('POSITIVE', 0.0)
    #     # agg_positive_by_bank_rating = aggregate_sentiments(
    #     #     data_with_sentiments,
    #     #     sentiment_score_key='positive_score', # Assuming you stored this
    #     #     group_by_columns=['bank', 'rating']
    #     # )
    #     # print(agg_positive_by_bank_rating.to_string())
