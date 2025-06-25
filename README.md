YouTube Comment Analyzer
A minimalist Streamlit web application designed to fetch comments from any public YouTube video, analyze their sentiment, extract key topics, and visualize these insights. Get a quick overview of how viewers feel and what they're discussing on YouTube videos.

✨ Features
Sentiment Analysis: Categorizes comments into Positive, Neutral, and Negative sentiments using NLTK's VADER.

Key Topic Extraction: Identifies and displays the top 10 most frequent and relevant keywords/topics discussed in the comments.

Interactive Visualizations:

Donut chart showing the distribution of Positive, Neutral, and Negative comments.

Horizontal bar chart visualizing the frequency of top keywords.

Data Export: Allows downloading of all fetched and analyzed comments, including sentiment scores, as a CSV file.

Optimized Performance: Fetches up to 35,000 comments, providing a comprehensive analysis (mindful of YouTube Data API quotas).

Clean UI: Minimalist and intuitive user interface for a smooth user experience, featuring a cream-colored background and prominent green action buttons.

🚀 Getting Started
Follow these steps to set up and run the YouTube Comment Analyzer locally on your machine.

Prerequisites
Python 3.8 or higher installed on your system.

pip (Python package installer).

A Google Cloud Project with the YouTube Data API v3 enabled.

A YouTube Data API Key. Learn how to get one here.

Installation
Clone the Repository:
Open your terminal or command prompt and clone the project to your local machine:

git clone https://github.com/Naman-aiml/youtube-comment-analyzer.git

Navigate to the Project Directory:

cd youtube-comment-analyzer

Create a Virtual Environment (Recommended):
This helps manage project dependencies cleanly.

python -m venv venv

Activate the Virtual Environment:

On Windows:

.\venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

Install Dependencies:
Install all required Python libraries using pip. If you don't have a requirements.txt file yet, you can install them manually:

pip install streamlit google-api-python-client nltk matplotlib

(If you'd like to create a requirements.txt file for easier installation in the future, let me know!)

Set Up Your YouTube Data API Key:
For local development, create a secrets file in your project:

Create a folder named .streamlit in the root of your youtube-comment-analyzer directory (if it doesn't already exist from theme setup).

Inside the .streamlit folder, create a file named secrets.toml.

Add your API key to secrets.toml like this (replace YOUR_YOUTUBE_API_KEY_HERE with your actual key):

# .streamlit/secrets.toml
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"

Important: Do NOT commit secrets.toml to your public GitHub repository! It should be in your .gitignore file to prevent accidental sharing of your private key.

Running the Application
Start the Streamlit App:
With your virtual environment activated, run the Streamlit application:

streamlit run youtube_app.py

If streamlit run is not found (e.g., CommandNotFoundException), try:

python -m streamlit run youtube_app.py

Your web browser will automatically open to the Streamlit app (usually http://localhost:8501).

👨‍💻 Usage
Enter a YouTube Video URL: In the input box on the web page, paste the full URL of the YouTube video you wish to analyze.

Click "Analyze Comments": The application will fetch comments (up to 35,000), perform sentiment analysis, and extract keywords.

View Results: The analyzed data, including sentiment distribution charts, top keywords table, and a bar chart, will be displayed in the main content area.

Download Data: Click the "Download Comments as CSV" button to get a CSV file of all fetched comments with their associated sentiment scores.


🤝 Contributing
Contributions are welcome! If you have suggestions for improvements or new features, please feel free to open an issue or submit a pull request.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
