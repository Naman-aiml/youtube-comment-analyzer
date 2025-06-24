import os
import googleapiclient.discovery
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re # For regular expressions to extract video ID
import csv # <--- ADDed THIS LINE
from nltk.corpus import stopwords # <--- ADD THIS LINE
from nltk.tokenize import word_tokenize # <--- ADD THIS LINE
from collections import Counter # <--- ADD THIS LINE (built-in Python module)
import matplotlib.pyplot as plt # <--- ADD THIS LINE

def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    # This regex handles various common YouTube URL formats
    match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})(?:&|\?)?', url)
    return match.group(1) if match else None

def get_youtube_comments(video_url, api_key, max_comments=100):
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

    comments = [] # List to store all fetched and analyzed comments
    next_page_token = None # Token for fetching next pages of comments
    comments_fetched_count = 0 # Counter for total comments fetched

    print(f"Fetching comments for video ID: {video_id}...")

    # Loop to fetch comments in chunks (up to 100 per request)
    # Continues until max_comments is reached or no more pages are available
    while comments_fetched_count < max_comments:
        try:
            # Construct the API request to list comment threads
            request = youtube.commentThreads().list(
                part="snippet", # Request the 'snippet' part to get comment text, author, etc.
                videoId=video_id,
                textFormat="plainText", # Get comments as plain text (removes HTML tags)
                # maxResults should not exceed 100 per API call
                maxResults=min(100, max_comments - comments_fetched_count),
                pageToken=next_page_token # Use the token to get the next page
            )
            response = request.execute() # Execute the API request

        except googleapiclient.errors.HttpError as e:
            # Catch specific HTTP errors from the API (e.g., 400 Bad Request, 403 Forbidden)
            print(f"API Error fetching comments: {e}")
            print("Possible reasons: Invalid video ID, comments disabled, or exceeded API quota.")
            return [] # Return empty list on API error

        except Exception as e:
            # Catch any other unexpected errors during the fetching process
            print(f"An unexpected error occurred during comment fetching: {e}")
            return [] # Return empty list on unexpected error

        # Process the comments from the current API response
        for item in response.get("items", []): # Safely get 'items' list; use empty list if 'items' not found
            try:
                # Extract the snippet for the top-level comment (ignoring replies for now)
                comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                comment_text = comment_snippet["textDisplay"]

                # Perform sentiment analysis using VADER on the comment text
                polarity_scores = analyzer.polarity_scores(comment_text)

                comments.append({
                    "author": comment_snippet["authorDisplayName"],
                    "text": comment_text,
                    "published_at": comment_snippet["publishedAt"],
                    "like_count": comment_snippet["likeCount"],
                    "sentiment_compound": polarity_scores['compound'], # Overall sentiment (-1 to +1)
                    "sentiment_pos": polarity_scores['pos'],          # Percentage of positive words
                    "sentiment_neu": polarity_scores['neu'],          # Percentage of neutral words
                    "sentiment_neg": polarity_scores['neg']           # Percentage of negative words
                })
                comments_fetched_count += 1
                if comments_fetched_count >= max_comments:
                    break # Stop if we've reached our desired max_comments

            except KeyError as e:
                # This catches cases where a comment item might be malformed or missing expected keys
                print(f"Warning: Skipping malformed comment item. Missing key: {e}. Item: {item}")
                continue # Continue to the next item

        # Get the token for the next page
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            # If no next page token, we've reached the end of available comments
            print("No more comments or reached end of available comments.")
            break # Exit the while loop

    print(f"Successfully fetched and analyzed {len(comments)} comments.")
    return comments # This must be the last line of the function, indented 4 spaces
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


# ... (The start of your if __name__ == "__main__": block will be after this) ...

    # Build the YouTube API client
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key
    )
# Initialize VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer() # <--- ADD THIS LIN
    comments = []
    next_page_token = None # Used for pagination to get more comments
    comments_fetched = 0

    print(f"Fetching comments for video ID: {video_id}...")

    # Loop to fetch comments in chunks until max_comments is reached or no more comments
    while comments_fetched < max_comments:
        # Construct the API request
        request = youtube.commentThreads().list(
            part="snippet", # We want the comment's content (snippet)
            videoId=video_id,
            textFormat="plainText", # Get comments as plain text, not HTML
            maxResults=min(500, max_comments - comments_fetched), # YouTube's max per request is 100
            pageToken=next_page_token # Use this to get the next page of comments
        )
        try:
            # Execute the request and get the response
            response = request.execute()
        except googleapiclient.errors.HttpError as e:
            # Handle potential API errors (like invalid key, quota exceeded, or invalid video ID)
            print(f"API Error: {e}")
            print("Possible issues: Incorrect API key, exceeded quota, or invalid video ID.")
            return [] # Exit if there's an API error

        # Process the comments from the current response
        for item in response.get("items", []): # Use .get() to safely access 'items'
            try:
                # Extract the top-level comment details (we're ignoring replies for now)
                comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                comment_text = comment_snippet["textDisplay"] # <--- MAKE SURE THIS LINE IS PRESENT

                # Perform sentiment analysis using VADER
                vs = analyzer.polarity_scores(comment_text) # <--- MAKE SURE THIS LINE IS PRESENT

                comments.append({
                    "author": comment_snippet["authorDisplayName"],
                    "text": comment_text,
                    "published_at": comment_snippet["publishedAt"],
                    "like_count": comment_snippet["likeCount"],
                    "sentiment_compound": vs['compound'], # <--- THESE 4 LINES ARE CRITICAL
                    "sentiment_pos": vs['pos'],
                    "sentiment_neu": vs['neu'],
                    "sentiment_neg": vs['neg']
                })
                comments_fetched += 1
                if comments_fetched >= max_comments:
                    break # Stop if we've reached our desired max_comments
            except KeyError as e:
                print(f"Warning: Skipping malformed comment item. Missing key: {e}")



        # Get the token for the next page, if available
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            # No more pages of comments, or we've reached the end
            print("No more comments or reached end of available comments.")
            break

    print(f"Successfully fetched {len(comments)} comments.")
    return comments

# This block runs only when the script is executed directly (not when imported as a module)
# ... (your existing code, functions, etc.) ...

# --- Main execution block when the script is run directly ---
if __name__ == "__main__":
    # Get API key from environment variable for security
    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set.")
        print("Please set it according to the instructions and restart your terminal.")
    else:
        # Prompt user for YouTube video URL
        video_url_input = input("Enter YouTube video URL: ")

        # Fetch and analyze comments
        # You can adjust max_comments to fetch more or fewer comments
        # Be mindful of YouTube Data API quota limits for larger numbers
        fetched_comments = get_youtube_comments(video_url_input, api_key, max_comments=100)

        if fetched_comments:
            # --- Display individual comments with sentiment (Preview first 10 for brevity) ---
            print("\n--- Fetched Comments (Preview with Sentiment) ---")
            # We explicitly slice [:10] here to avoid overwhelming the terminal with too many comments
            for i, comment_data in enumerate(fetched_comments[:10]):
                print(f"\n--- Comment {i+1} ---")
                print(f"Text: {comment_data['text']}")
                print(f"Sentiment (Compound): {comment_data['sentiment_compound']:.2f}")
                print(f"Sentiment (Pos/Neu/Neg): {comment_data['sentiment_pos']:.2f}/{comment_data['sentiment_neu']:.2f}/{comment_data['sentiment_neg']:.2f}")
            
            # --- Overall Sentiment Summary ---
            # Calculate overall sentiment statistics from all fetched comments
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
            # Prepare data for the pie chart
            sentiment_labels = ['Positive', 'Neutral', 'Negative']
            sentiment_counts = [len(positive_comments), len(neutral_comments), len(negative_comments)]
            # Define colors for the pie chart slices
            colors = ['#4CAF50', '#FFC107', '#F44336'] # Green for Positive, Amber for Neutral, Red for Negative

            # Create the pie chart figure and axes
            fig, ax = plt.subplots(figsize=(8, 8)) # Set figure size for better readability
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
            if top_keywords: # Only create chart if keywords were found
                # Prepare data for the horizontal bar chart
                keywords = [item[0] for item in top_keywords] # List of just the keyword strings
                counts = [item[1] for item in top_keywords] # List of just the counts

                # Create the bar chart figure and axes
                # Adjust height based on number of keywords for better readability
                fig_bar, ax_bar = plt.subplots(figsize=(10, max(6, len(keywords) * 0.6)))
                # Plot horizontal bars
                ax_bar.barh(keywords, counts, color='skyblue')

                # Set labels and title
                ax_bar.set_xlabel('Frequency', fontsize=12)
                ax_bar.set_ylabel('Keywords', fontsize=12)
                ax_bar.set_title('Top Keywords/Topics in Comments', fontsize=16)
                ax_bar.invert_yaxis() # Invert y-axis to put the highest count keyword at the top

                plt.tight_layout() # Adjust layout to prevent labels/titles from overlapping or being cut off

                # Define the path and save the chart as a PNG image
                keywords_chart_path = "top_keywords_bar_chart.png"
                plt.savefig(keywords_chart_path, bbox_inches='tight', dpi=100)
                print(f"\nTop keywords bar chart saved to {keywords_chart_path}")
                plt.close(fig_bar) # Close the plot to free up memory
            else:
                print("No meaningful keywords to visualize.")

            # --- Save Comments to CSV ---
            # Define the path for the CSV file
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

