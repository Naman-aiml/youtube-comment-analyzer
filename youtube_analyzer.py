import os
import googleapiclient.discovery
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re 
import csv 
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from collections import Counter 
import matplotlib.pyplot as plt

def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    # This regex handles various common YouTube URL formats
    match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})(?:&|\?)?', url)
    return match.group(1) if match else None

def get_youtube_comments(video_url, api_key, max_comments=1500):
    """
    Fetches comments for a given YouTube video URL, performs sentiment analysis
    on each comment, and returns a list of dictionaries with comment details
    and sentiment scores.
    Handles pagination to fetch up to max_comments.
    """
    video_id = get_video_id(video_url)
    if not video_id:
        print("Error: Could not extract a valid video ID from the provided URL.")
        return [] # Return an empty list if URL is invalid

    # Build the YouTube API client
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key
    )
    # Initialize VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    comments = [] 
    next_page_token = None 
    comments_fetched_count = 0 

    print(f"Fetching comments for video ID: {video_id}...")

    # 
    # Continues until max_comments is reached or no more pages are available
    while comments_fetched_count < max_comments:
        try:
            # Construct the API request to list comment threads
            request = youtube.commentThreads().list(
                part="snippet", 
                videoId=video_id,
                textFormat="plainText", 
                maxResults=min(1500, max_comments - comments_fetched_count),
                pageToken=next_page_token 
            )
            response = request.execute() # Execute the API request

        except googleapiclient.errors.HttpError as e:
            # Catch specific HTTP errors from the API (e.g., 400 Bad Request, 403 Forbidden)
            print(f"API Error fetching comments: {e}")
            print("Possible reasons: Invalid video ID, comments disabled, or exceeded API quota.")
            return []

        except Exception as e:
        
            print(f"An unexpected error occurred during comment fetching: {e}")
            return [] 

        # Process the comments from the current API response
        for item in response.get("items", []): 
            try:
                
                comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                comment_text = comment_snippet["textDisplay"]

                # Perform sentiment analysis using VADER on the comment text
                polarity_scores = analyzer.polarity_scores(comment_text)

                comments.append({
                    "author": comment_snippet["authorDisplayName"],
                    "text": comment_text,
                    "published_at": comment_snippet["publishedAt"],
                    "like_count": comment_snippet["likeCount"],
                    "sentiment_compound": polarity_scores['compound'],
                    "sentiment_pos": polarity_scores['pos'],     
                    "sentiment_neu": polarity_scores['neu'],       
                    "sentiment_neg": polarity_scores['neg']           
                })
                comments_fetched_count += 1
                if comments_fetched_count >= max_comments:
                    break # Stop if we've reached our desired max_comments

            except KeyError as e:
                # This catches cases where a comment item might be malformed or missing expected keys
                print(f"Warning: Skipping malformed comment item. Missing key: {e}. Item: {item}")
                continue 

        # Get the token for the next page
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
           
            print("No more comments or reached end of available comments.")
            break 

    print(f"Successfully fetched and analyzed {len(comments)} comments.")
    return comments 
def extract_keywords(comments, num_keywords=10):
    all_words = []
    stop_words = set(stopwords.words('english'))

    for comment in comments:
        text = comment['text'].lower()
        words = word_tokenize(re.sub(r'[^a-zA-Z\s]', '', text))
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
        all_words.extend(filtered_words)

    word_counts = Counter(all_words)
    return word_counts.most_common(num_keywords)


# --- Main execution block when the script is run directly ---
if __name__ == "__main__":
    # Get API key from environment variable for security
    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set.")
        print("Please set it according to the instructions and restart your terminal.")
    else:
        video_url_input = input("Enter YouTube video URL: ")

        
        # Be mindful of YouTube Data API quota limits for larger numbers
        fetched_comments = get_youtube_comments(video_url_input, api_key, max_comments=1500)

        if fetched_comments:
            print("\n--- Fetched Comments (Preview with Sentiment) ---")
            # We explicitly slice [:10] here to avoid overwhelming the terminal with too many comments
            for i, comment_data in enumerate(fetched_comments[:10]):
                print(f"\n--- Comment {i+1} ---")
                print(f"Text: {comment_data['text']}")
                print(f"Sentiment (Compound): {comment_data['sentiment_compound']:.2f}")
                print(f"Sentiment (Pos/Neu/Neg): {comment_data['sentiment_pos']:.2f}/{comment_data['sentiment_neu']:.2f}/{comment_data['sentiment_neg']:.2f}")
            
            # --- Overall Sentiment Summary ---
            total_compound_score = sum(c['sentiment_compound'] for c in fetched_comments)
            average_compound_score = total_compound_score / len(fetched_comments)

            # Categorize comments based on VADER's typical thresholds for positive, neutral, negative
            # A compound score >= 0.05 is generally considered positive
            # A compound score <= -0.05 is generally considered negative
            # Scores between -0.05 and 0.05 are considered neutral
            positive_comments = [c for c in fetched_comments if c['sentiment_compound'] >= 0.05]
            neutral_comments = [c for c in fetched_comments if c['sentiment_compound'] > -0.05 and c['sentiment_compound'] < 0.05]
            negative_comments = [c for c in fetched_comments if c['sentiment_compound'] <= -0.05]

            print("\n--- Overall Sentiment Summary ---")
            print(f"Total Comments Analyzed: {len(fetched_comments)}")
            print(f"Average Compound Sentiment Score: {average_compound_score:.2f}")
            print(f"Positive Comments: {len(positive_comments)} ({(len(positive_comments)/len(fetched_comments))*100:.1f}%)")
            print(f"Neutral Comments: {len(neutral_comments)} ({(len(neutral_comments)/len(fetched_comments))*100:.1f}%)")
            print(f"Negative Comments: {len(negative_comments)} ({(len(negative_comments)/len(fetched_comments))*100:.1f}%)")

            # --- Visualize Sentiment Distribution (Pie Chart) ---
            sentiment_labels = ['Positive', 'Neutral', 'Negative']
            sentiment_counts = [len(positive_comments), len(neutral_comments), len(negative_comments)]
            colors = ['#4CAF50', '#FFC107', '#F44336'] # Green for Positive, Amber for Neutral, Red for Negative

            # Create the pie chart figure and axes
            fig, ax = plt.subplots(figsize=(8, 8)) 
            # Plot the pie chart
            wedges, texts, autotexts = ax.pie(
                sentiment_counts,
                labels=sentiment_labels,
                autopct='%1.1f%%', # Format percentages on slices (e.g., "74.1%")
                colors=colors,
                startangle=90, # Start the first slice (Positive) at the top
                pctdistance=0.85 # Distance of percentage labels from the center of the pie
            )

            # Add a white circle to the center to create a donut chart effect
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig.gca().add_artist(centre_circle)

            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a perfect circle.
            ax.set_title('Overall Comment Sentiment Distribution', fontsize=16) # Set chart title

            # Define the path and save the chart as a PNG image
            sentiment_chart_path = "sentiment_distribution_pie_chart.png"
            plt.savefig(sentiment_chart_path, bbox_inches='tight', dpi=100) # bbox_inches='tight' prevents labels from being cut off
            print(f"\nSentiment distribution pie chart saved to {sentiment_chart_path}")
            plt.close(fig) # Close the plot to free up memory and prevent display issues in CLI

            # --- Keyword/Topic Extraction Summary ---
            # Extract top keywords from all fetched comments
            top_keywords = extract_keywords(fetched_comments, num_keywords=15) # Get top 15 keywords
            print("\n--- Top Keywords/Topics ---")
            if top_keywords:
                for keyword, count in top_keywords:
                    print(f"- {keyword}: {count}")
            else:
                print("No meaningful keywords found.")

            # --- Visualize Top Keywords (Bar Chart) ---
            if top_keywords:
                keywords = [item[0] for item in top_keywords] 
                counts = [item[1] for item in top_keywords] 

                # Create the bar chart figure and axes
                # Adjust height based on number of keywords for better readability
                fig_bar, ax_bar = plt.subplots(figsize=(10, max(6, len(keywords) * 0.6)))
                # Plot horizontal bars
                ax_bar.barh(keywords, counts, color='skyblue')

                # Set labels and title
                ax_bar.set_xlabel('Frequency', fontsize=12)
                ax_bar.set_ylabel('Keywords', fontsize=12)
                ax_bar.set_title('Top Keywords/Topics in Comments', fontsize=16)
                ax_bar.invert_yaxis() 

                plt.tight_layout()

                # Define the path and save the chart as a PNG image
                keywords_chart_path = "top_keywords_bar_chart.png"
                plt.savefig(keywords_chart_path, bbox_inches='tight', dpi=100)
                print(f"\nTop keywords bar chart saved to {keywords_chart_path}")
                plt.close(fig_bar) 
            else:
                print("No meaningful keywords to visualize.")

            # --- Save Comments to CSV ---
    
            csv_file_path = "youtube_comments_with_sentiment.csv"
            # Define the headers for the CSV file, matching the dictionary keys
            fieldnames = [
                "author", "text", "published_at", "like_count",
                "sentiment_compound", "sentiment_pos", "sentiment_neu", "sentiment_neg"
            ]
            try:
                # Open the CSV file in write mode ('w'), with no extra blank rows (newline=''), and UTF-8 encoding
                with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader() # Write the header row
                    writer.writerows(fetched_comments) # Write all comment dictionaries as rows
                print(f"\nSuccessfully saved {len(fetched_comments)} comments to {csv_file_path}")
            except Exception as e:
                # Catch and print any errors that occur during file saving
                print(f"\nError saving comments to CSV: {e}")

        else: # This block executes if 'fetched_comments' list is empty (e.g., invalid URL, API error, no comments found)
            print("\nNo comments were fetched or analyzed. Please check the video URL, your API key, or your quota.")

