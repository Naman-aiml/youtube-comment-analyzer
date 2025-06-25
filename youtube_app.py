import streamlit as st
import os
import nltk
from youtube_analyzer import get_video_id, get_youtube_comments, extract_keywords
import matplotlib.pyplot as plt
import csv
import io # Ensure 'io' is imported for CSV download functionality

# --- NLTK Data Download (for Streamlit Cloud deployment - Streamlit's recommended way) ---
# Downloads all commonly used NLTK data. This should cover punkt, vader, and stopwords.
nltk.download('all')
# Note: For local development, if you encounter PermissionError, ensure VS Code is run as Administrator.

# --- Streamlit App Configuration and Initial UI ---
# Set page configuration for the Streamlit app
# layout="centered" puts content in a central column, but charts/tables can expand with use_container_width=True.
st.set_page_config(page_title="YouTube Comment Analyzer", layout="centered")

# Set custom theme colors via .streamlit/config.toml
# You've already set these:
# Background: #FDFBF7 (light cream)
# Primary (button): #4CAF50 (green)
# Text: #262730

# Main title and description for the application
st.title("YouTube Comment Analyzer")
st.write("Enter a YouTube video URL to analyze its comments for sentiment and keywords. This app fetches up to 10,000 comments.")

# --- Custom Centered and Styled Label ---
# Use columns to effectively center the "YouTube Video URL:" text
col_left_space, col_label_center, col_right_space = st.columns([1, 4, 1])

with col_label_center:
    # Using Markdown with HTML for custom styling: center text, large size, and a vibrant orange-red color.
    st.markdown("<h2 style='text-align: center; color: #FF4500; font-size: 3em;'>YouTube Video URL:</h2>", unsafe_allow_html=True)

# --- Input Field and Analyze Button (Layout remains side-by-side) ---
# Use columns for horizontal layout: input field is wider than the button
col_input, col_button = st.columns([3, 1]) # 3:1 ratio means input takes 3/4th width, button takes 1/4th

with col_input:
    # The text input field. Label is empty as we provided a custom Markdown label above.
    video_url = st.text_input(label="", help="Paste the full YouTube video link here.", key="youtube_url_input")

with col_button:
    # Add an empty markdown element for vertical alignment of the button with the text input.
    st.write("")
    # The "Analyze Comments" button. Its color is controlled by primaryColor in config.toml.
    # The key is crucial for Streamlit to uniquely identify this widget.
    if st.button("Analyze Comments", key="analyze_button"):
        # This 'if' block now primarily serves to trigger a script rerun when the button is clicked.
        # The actual analysis and display logic is handled by the top-level 'if video_url:' block below.
        pass


# --- ALL ANALYSIS OUTPUT (THIS IS THE KEY CHANGE FOR WIDE/CENTERED DISPLAY) ---
# This entire block of code is at the top-level indentation (no leading spaces).
# This ensures it uses the full available width of the Streamlit page.
if video_url: # This 'if' must be at the top-level indentation (aligned with st.title, st.columns, etc.).

    # Display analysis initiation message
    st.info(f"Starting analysis for: {video_url}...")

    # Safely retrieve the API key from Streamlit secrets (for deployed apps)
    # or from environment variables (for local testing).
    api_key = st.secrets.get("YOUTUBE_API_KEY", os.getenv("YOUTUBE_API_KEY"))

    if not api_key:
        # Display an error if the API key is not found
        st.error("Error: YOUTUBE_API_KEY environment variable not set. Please set it securely in Streamlit Cloud secrets or locally in .streamlit/secrets.toml.")
    else:
        # Use st.spinner to show a loading indicator while comments are being fetched and analyzed.
        with st.spinner('Fetching and analyzing comments... This might take a moment depending on the video.'):
            # Call the core function from youtube_analyzer.py to fetch comments.
            # max_comments set to 35,000 as requested, but be mindful of YouTube Data API quota limits.
            fetched_comments = get_youtube_comments(video_url, api_key, max_comments=35000)

        if fetched_comments:
            # Display success message after fetching comments
            st.success(f"Successfully fetched and analyzed {len(fetched_comments)} comments!")

            # --- Overall Sentiment Summary Display ---
            # Using st.expander to make this section collapsible, keeping the UI clean.
            # It starts expanded by default (expanded=True).
            with st.expander("Click to view Overall Sentiment Summary", expanded=True):
                st.subheader("Overall Sentiment Summary")
                # Calculate total and average compound sentiment scores
                total_compound_score = sum(c['sentiment_compound'] for c in fetched_comments)
                average_compound_score = total_compound_score / len(fetched_comments)

                # Categorize comments based on VADER's standard thresholds for sentiment
                positive_comments = [c for c in fetched_comments if c['sentiment_compound'] >= 0.05]
                neutral_comments = [c for c in fetched_comments if c['sentiment_compound'] > -0.05 and c['sentiment_compound'] < 0.05]
                negative_comments = [c for c in fetched_comments if c['sentiment_compound'] <= -0.05]

                # Display sentiment metrics using f-strings for formatted output
                st.write(f"**Total Comments Analyzed:** {len(fetched_comments)}")
                st.write(f"**Average Compound Sentiment Score:** {average_compound_score:.2f}")
                st.write(f"**Positive Comments:** {len(positive_comments)} ({(len(positive_comments)/len(fetched_comments))*100:.1f}%)")
                st.write(f"**Neutral Comments:** {len(neutral_comments)} ({(len(neutral_comments)/len(fetched_comments))*100:.1f}%)")
                st.write(f"**Negative Comments:** {len(negative_comments)} ({(len(negative_comments)/len(fetched_comments))*100:.1f}%)")

            # --- Sentiment Distribution Pie Chart ---
            st.subheader("Sentiment Distribution")
            sentiment_labels = ['Positive', 'Neutral', 'Negative']
            sentiment_counts = [len(positive_comments), len(neutral_comments), len(negative_comments)]
            colors = ['#4CAF50', '#FFC107', '#F44336'] # Green, Amber, Red for sentiment slices

            # Create the Matplotlib figure and axes for the pie chart
            fig, ax = plt.subplots(figsize=(8, 8)) # Fixed size for the pie chart for consistency
            ax.pie(
                sentiment_counts,
                labels=sentiment_labels,
                autopct='%1.1f%%', # Format percentages (e.g., "40.0%")
                colors=colors,
                startangle=90, # Start the first slice (Positive) at the top (12 o'clock)
                pctdistance=0.85 # Distance of percentage labels from the center of the pie
            )
            # Add a white circle in the center to create a donut chart effect
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig.gca().add_artist(centre_circle) # Add the circle to the current axes of the figure
            ax.axis('equal') # Ensure pie is drawn as a perfect circle, not an ellipse
            ax.set_title('Overall Comment Sentiment Distribution', fontsize=16)
            st.pyplot(fig) # Display the matplotlib figure in Streamlit
            plt.close(fig) # Close the figure to free memory and prevent display issues

            # --- Top Keywords/Topics Display and Bar Chart ---
            st.subheader("Top Keywords/Topics")
            # Extract top keywords using the function from youtube_analyzer.py
            top_keywords = extract_keywords(fetched_comments, num_keywords=10) # Set to 10 keywords as requested
            if top_keywords:
                # Prepare keyword data for display in a Streamlit dataframe (tabular view)
                keywords_display_data = [{"Keyword": kw, "Frequency": freq} for kw, freq in top_keywords]
                # use_container_width=True makes the dataframe expand to the available width.
                st.dataframe(keywords_display_data, use_container_width=True, hide_index=True)

                # Prepare data for the horizontal bar chart
                keywords = [item[0] for item in top_keywords]
                counts = [item[1] for item in top_keywords]

                # Create the bar chart figure
                # Dynamically adjust figure height based on the number of keywords to prevent overlap.
                fig_bar, ax_bar = plt.subplots(figsize=(10, max(6, len(keywords) * 0.5)))
                ax_bar.barh(keywords, counts, color='skyblue') # Use barh for horizontal bars
                ax_bar.set_xlabel('Frequency', fontsize=12)
                ax_bar.set_ylabel('Keywords', fontsize=12)
                ax_bar.set_title('Top Keywords/Topics in Comments', fontsize=16)
                ax_bar.invert_yaxis() # Invert Y-axis to show the highest count keyword at the top of the chart (more intuitive ranking)
                plt.tight_layout() # Adjusts plot parameters for a tight layout, preventing labels from overlapping
                st.pyplot(fig_bar) # Display the bar chart in Streamlit
                plt.close(fig_bar) # Close the figure

            else:
                st.write("No meaningful keywords found for analysis.")

            # --- Download Comments as CSV Button ---
            # This section creates CSV data in memory and provides a download button.
            csv_data_string = ""
            fieldnames = [
                "author", "text", "published_at", "like_count",
                "sentiment_compound", "sentiment_pos", "sentiment_neu", "sentiment_neg"
            ]

            # Use io.StringIO to write CSV data to a string buffer in memory
            writer_output = io.StringIO() # Changed variable name to avoid potential conflict if any
            writer = csv.DictWriter(writer_output, fieldnames=fieldnames)
            writer.writeheader() # Write the column headers
            writer.writerows(fetched_comments) # Write the comment data rows
            csv_data_string = writer_output.getvalue() # Get the full CSV string
            writer_output.close() # Close the string buffer

            # Display the download button
            st.download_button(
                label="Download Comments as CSV", # Text displayed on the button
                data=csv_data_string, # The actual CSV data
                file_name="youtube_comments_with_sentiment.csv", # Default file name for download
                mime="text/csv", # MIME type for CSV files
                use_container_width=True # Make the button stretch to the full available width
            )

        else: # If get_youtube_comments returned an empty list of comments (e.g., no comments, video error, quota)
            st.warning("No comments were fetched for this video. Please check the URL, if the video has comments enabled, your API key, or your daily API quota.")
else: # This 'else' corresponds to the top-level 'if video_url:' block.
    # This message appears when the app first loads or if the URL input is empty and Analyze is clicked.
    st.write("") # Add a spacer for better visual separation.
    # Optionally, add a helpful instruction: st.info("Enter a YouTube video URL and click 'Analyze Comments' to get started!")
