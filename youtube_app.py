import streamlit as st
import os # Needed to get the API key

# Import your functions from the youtube_analyzer.py file
# Ensure youtube_analyzer.py is in the same directory as youtube_app.py
from youtube_analyzer import get_video_id, get_youtube_comments, extract_keywords

# You might also need to import matplotlib here if your youtube_analyzer.py doesn't
# save plots directly and you want to display them interactively in Streamlit.
# For now, we assume your analyzer saves them and we'll display the saved image.
# If your analyzer.py *doesn't* contain 'import matplotlib.pyplot as plt', add it here.
import matplotlib.pyplot as plt # Needed for plotting directly in Streamlit if we change that later

# Set the title and layout of your web application
st.set_page_config(page_title="YouTube Comment Analyzer", layout="centered")

st.title("YouTube Comment Analyzer")
st.write("Enter a YouTube video URL to analyze its comments for sentiment and keywords.")

# Input field for the YouTube video URL
video_url = st.text_input("YouTube Video URL:", help="Paste the full YouTube video link here.", key="youtube_url_input")

# Button to trigger the analysis
if st.button("Analyze Comments",key="analyze_button"):
    if video_url: # Check if a URL was provided
        st.info(f"Analyzing comments for: {video_url}")
        # This is where we will call our backend analysis function later
        st.success("Analysis initiated (backend integration coming soon!).")
    else:
        st.warning("Please enter a YouTube video URL to proceed.")
# ... (rest of your existing youtube_app.py code above this block) ...

# Input field for the YouTube video URL

    if video_url: # Check if a URL was provided
        st.info(f"Starting analysis for: {video_url}...")

       # Safely get the API key from Streamlit secrets (for deployment)
# Fallback to os.getenv for local testing if preferred
        api_key = st.secrets.get("YOUTUBE_API_KEY", os.getenv("YOUTUBE_API_KEY"))
        if not api_key:
            st.error("Error: YOUTUBE_API_KEY environment variable not set. Please set it.")
        else:
            # Call the comment fetching and analysis function
            # Consider adding a spinner for better UX for long waits
            with st.spinner('Fetching and analyzing comments... This might take a moment.'):
                # In a real app, you might want to increase max_comments beyond 100
                # Be mindful of YouTube API quota. 500-1000 comments is a good balance for typical free tier.
                fetched_comments = get_youtube_comments(video_url, api_key, max_comments=100) # Max 100 for quick test

            if fetched_comments:
                st.success(f"Successfully fetched and analyzed {len(fetched_comments)} comments!")

                # --- Display Overall Sentiment Summary ---
                total_compound_score = sum(c['sentiment_compound'] for c in fetched_comments)
                average_compound_score = total_compound_score / len(fetched_comments)

                positive_comments = [c for c in fetched_comments if c['sentiment_compound'] >= 0.05]
                neutral_comments = [c for c in fetched_comments if c['sentiment_compound'] > -0.05 and c['sentiment_compound'] < 0.05]
                negative_comments = [c for c in fetched_comments if c['sentiment_compound'] <= -0.05]

                st.subheader("Overall Sentiment Summary")
                st.write(f"**Total Comments Analyzed:** {len(fetched_comments)}")
                st.write(f"**Average Compound Sentiment Score:** {average_compound_score:.2f}")
                st.write(f"**Positive Comments:** {len(positive_comments)} ({(len(positive_comments)/len(fetched_comments))*100:.1f}%)")
                st.write(f"**Neutral Comments:** {len(neutral_comments)} ({(len(neutral_comments)/len(fetched_comments))*100:.1f}%)")
                st.write(f"**Negative Comments:** {len(negative_comments)} ({(len(negative_comments)/len(fetched_comments))*100:.1f}%)")

                # --- Display Sentiment Pie Chart ---
                st.subheader("Sentiment Distribution")
                sentiment_labels = ['Positive', 'Neutral', 'Negative']
                sentiment_counts = [len(positive_comments), len(neutral_comments), len(negative_comments)]
                colors = ['#4CAF50', '#FFC107', '#F44336']

                fig, ax = plt.subplots(figsize=(8, 8))
                wedges, texts, autotexts = ax.pie(
                    sentiment_counts,
                    labels=sentiment_labels,
                    autopct='%1.1f%%',
                    colors=colors,
                    startangle=90,
                    pctdistance=0.85
                )
                centre_circle = plt.Circle((0,0),0.70,fc='white')
                fig.gca().add_artist(centre_circle)
                ax.axis('equal')
                ax.set_title('Overall Comment Sentiment Distribution', fontsize=16)
                st.pyplot(fig) # Display the plot in Streamlit
                plt.close(fig) # Close the plot after displaying

                # --- Display Top Keywords ---
                st.subheader("Top Keywords/Topics")
                top_keywords = extract_keywords(fetched_comments, num_keywords=15)
                if top_keywords:
                    keywords_df = st.dataframe(top_keywords, use_container_width=True, hide_index=True) # Display as a table
                    # Also display as a bar chart
                    keywords = [item[0] for item in top_keywords]
                    counts = [item[1] for item in top_keywords]

                    fig_bar, ax_bar = plt.subplots(figsize=(10, max(6, len(keywords) * 0.5)))
                    ax_bar.barh(keywords, counts, color='skyblue')
                    ax_bar.set_xlabel('Frequency', fontsize=12)
                    ax_bar.set_ylabel('Keywords', fontsize=12)
                    ax_bar.set_title('Top Keywords/Topics in Comments', fontsize=16)
                    ax_bar.invert_yaxis()
                    plt.tight_layout()
                    st.pyplot(fig_bar) # Display the bar chart in Streamlit
                    plt.close(fig_bar)
                else:
                    st.write("No meaningful keywords found.")

                # --- Option to Download CSV ---
                # To download, we need to read the CSV content and provide it.
                # Your youtube_analyzer.py still saves the CSV, so we'll just read that for download
                csv_file_path = "youtube_comments_with_sentiment.csv"
                if os.path.exists(csv_file_path):
                    with open(csv_file_path, "rb") as file: # "rb" for read binary
                        btn = st.download_button(
                            label="Download Comments as CSV",
                            data=file,
                            file_name="youtube_comments_with_sentiment.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("No comments were fetched or analyzed. Please check the video URL, your API key, or your quota.")
    else:
        st.warning("Please enter a YouTube video URL to proceed.")