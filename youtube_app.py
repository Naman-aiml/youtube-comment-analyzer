import streamlit as st
import os
import nltk 
from youtube_analyzer import get_video_id, get_youtube_comments, extract_keywords
import matplotlib.pyplot as plt
import csv # Required for the st.download_button functionality


# --- NLTK Data Download (for Streamlit Cloud deployment - Direct Approach) ---
# This directly calls nltk.download. Streamlit will cache these downloads.
# We remove the problematic 'try...except nltk.downloader.DownloadError'
# as it seems to be causing an AttributeError on Streamlit Cloud.
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')
# --- End NLTK Data Download ---

# --- Streamlit App Configuration and Initial UI ---
# Set page configuration for the Streamlit app. This should be at the top level.
st.set_page_config(page_title="YouTube Comment Analyzer", layout="centered")

# Main title and description for the application
st.title("YouTube Comment Analyzer")
st.write("Enter a YouTube video URL to analyze its comments for sentiment and keywords. This app fetches up to 100 comments.")

# --- User Input Section ---
# Text input field for the YouTube video URL. A unique 'key' is crucial for Streamlit widgets.
video_url = st.text_input("YouTube Video URL:", help="Paste the full YouTube video link here.", key="youtube_url_input")

# Button to trigger the analysis. A unique 'key' is also required for buttons.
if st.button("Analyze Comments", key="analyze_button"):
    # This entire block below will execute only when the "Analyze Comments" button is clicked.
    if video_url: # Ensure a URL has been provided by the user
        st.info(f"Starting analysis for: {video_url}...")

        # --- API Key Retrieval ---
        # Safely get the API key. It first checks Streamlit secrets (for deployed apps),
        # then falls back to environment variables (for local testing).
        api_key = st.secrets.get("YOUTUBE_API_KEY", os.getenv("YOUTUBE_API_KEY"))

        if not api_key:
            # Display an error if the API key is not set
            st.error("Error: YOUTUBE_API_KEY environment variable not set. Please set it securely in Streamlit Cloud secrets or locally.")
        else:
            # --- Fetching and Analyzing Comments ---
            # Display a spinner to indicate that a long-running process is underway
            with st.spinner('Fetching and analyzing comments... This might take a moment.'):
                # Call the core function from youtube_analyzer.py
                # max_comments can be adjusted, but be mindful of YouTube Data API quota limits.
                fetched_comments = get_youtube_comments(video_url, api_key, max_comments=100)

            if fetched_comments:
                st.success(f"Successfully fetched and analyzed {len(fetched_comments)} comments!")

                # --- Overall Sentiment Summary Display ---
                st.subheader("Overall Sentiment Summary")
                total_compound_score = sum(c['sentiment_compound'] for c in fetched_comments)
                average_compound_score = total_compound_score / len(fetched_comments)

                # Categorize comments based on VADER's standard thresholds for sentiment
                positive_comments = [c for c in fetched_comments if c['sentiment_compound'] >= 0.05]
                neutral_comments = [c for c in fetched_comments if c['sentiment_compound'] > -0.05 and c['sentiment_compound'] < 0.05]
                negative_comments = [c for c in fetched_comments if c['sentiment_compound'] <= -0.05]

                st.write(f"**Total Comments Analyzed:** {len(fetched_comments)}")
                st.write(f"**Average Compound Sentiment Score:** {average_compound_score:.2f}")
                st.write(f"**Positive Comments:** {len(positive_comments)} ({(len(positive_comments)/len(fetched_comments))*100:.1f}%)")
                st.write(f"**Neutral Comments:** {len(neutral_comments)} ({(len(neutral_comments)/len(fetched_comments))*100:.1f}%)")
                st.write(f"**Negative Comments:** {len(negative_comments)} ({(len(negative_comments)/len(fetched_comments))*100:.1f}%)")

                # --- Sentiment Distribution Pie Chart ---
                st.subheader("Sentiment Distribution")
                sentiment_labels = ['Positive', 'Neutral', 'Negative']
                sentiment_counts = [len(positive_comments), len(neutral_comments), len(negative_comments)]
                colors = ['#4CAF50', '#FFC107', '#F44336'] # Define colors for chart slices

                # Create the Matplotlib figure and axes for the pie chart
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(
                    sentiment_counts,
                    labels=sentiment_labels,
                    autopct='%1.1f%%', # Format percentages
                    colors=colors,
                    startangle=90, # Start the first slice at the top
                    pctdistance=0.85 # Distance of percentage labels from center
                )
                centre_circle = plt.Circle((0,0),0.70,fc='white') # Add a white circle for donut effect
                fig.gca().add_artist(centre_circle)
                ax.axis('equal') # Ensure pie is drawn as a perfect circle
                ax.set_title('Overall Comment Sentiment Distribution', fontsize=16)
                st.pyplot(fig) # Display the Matplotlib figure in Streamlit
                plt.close(fig) # Close the figure to free memory and prevent display issues

                # --- Top Keywords/Topics Display and Bar Chart ---
                st.subheader("Top Keywords/Topics")
                # Call the keyword extraction function from youtube_analyzer.py
                top_keywords = extract_keywords(fetched_comments, num_keywords=15)
                if top_keywords:
                    # Display keywords in a Streamlit dataframe for a clean tabular view
                    # Convert list of tuples to a format st.dataframe can better display with custom columns
                    keywords_display_data = [{"Keyword": kw, "Frequency": freq} for kw, freq in top_keywords]
                    st.dataframe(keywords_display_data, use_container_width=True, hide_index=True)

                    # Create and display a horizontal bar chart for keyword frequencies
                    keywords = [item[0] for item in top_keywords]
                    counts = [item[1] for item in top_keywords]

                    fig_bar, ax_bar = plt.subplots(figsize=(10, max(6, len(keywords) * 0.5))) # Dynamic height based on number of keywords
                    ax_bar.barh(keywords, counts, color='skyblue') # Horizontal bar chart
                    ax_bar.set_xlabel('Frequency', fontsize=12)
                    ax_bar.set_ylabel('Keywords', fontsize=12)
                    ax_bar.set_title('Top Keywords/Topics in Comments', fontsize=16)
                    ax_bar.invert_yaxis() # Puts the highest count keyword at the top of the chart
                    plt.tight_layout() # Adjusts plot parameters for a tight layout
                    st.pyplot(fig_bar) # Display the bar chart in Streamlit
                    plt.close(fig_bar) # Close the figure

                else:
                    st.write("No meaningful keywords found for analysis.")

                # --- Download Comments as CSV Button ---
                # This creates CSV data in memory and allows the user to download it directly.
                csv_data_string = ""
                fieldnames = [
                    "author", "text", "published_at", "like_count",
                    "sentiment_compound", "sentiment_pos", "sentiment_neu", "sentiment_neg"
                ]
                
                # Use io.StringIO to write CSV data to a string in memory
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(fetched_comments)
                csv_data_string = output.getvalue()
                output.close()

                st.download_button(
                    label="Download Comments as CSV",
                    data=csv_data_string,
                    file_name="youtube_comments_with_sentiment.csv",
                    mime="text/csv"
                )

            else: # If get_youtube_comments returned an empty list
                st.warning("No comments were fetched for this video. Please check the URL, if the video has comments enabled, your API key, or your daily API quota.")
    else: # If the Analyze button was clicked but no URL was entered
        st.warning("Please enter a YouTube video URL to proceed with the analysis.")

# --- End of Streamlit App Code ---