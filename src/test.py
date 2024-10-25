import openai
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Replace 'your-api-key' with your actual OpenAI API key
openai.api_key = 'insert the chartmetric openai api key'

# Check if the API key is set correctly
if openai.api_key is None:
    print("API key not found.")
else:
    print("API key loaded successfully.")
# Load label websites from Labels.csv
def load_labels(file_path):
    labels_df = pd.read_csv(file_path)
    print(labels_df.columns)  # This will display the column names
    return labels_df

# Use OpenAI to extract artist names from HTML content
def extract_artist_names(html_content):
    prompt = (f"Extract only the artist names from the following HTML content. "
          f"The artist names are primarily found in <a> and <h3> tags. "
          f"Return the names as a comma-separated list with no introductory text or extra information: {html_content[:2000]}")
        
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error processing with OpenAI: {e}")
        return None

# Fetch HTML content from the given URL
def fetch_html_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to fetch {url}: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    # Load the label websites from Labels.csv
    labels_df = load_labels('data/Labels.csv')

    all_artists = []

    # Loop through each label's URL and extract artist names
    for index, row in labels_df.iterrows():
        label_name = row['Label Name']
        url = row['URL']  # Change 'ArtistPageURL' to 'URL'
        
        print(f"Processing {label_name} at {url}...")
        html_content = fetch_html_content(url)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Use OpenAI to extract artist names
            artist_names = extract_artist_names(str(soup))
            if artist_names:
                print(f"Extracted artists for {label_name}: {artist_names}")
                all_artists.append({'Label Name': label_name, 'Artists': artist_names})

    # Convert to DataFrame and save the results
    df_artists = pd.DataFrame(all_artists)
    df_artists.to_csv('data/extracted_artists.csv', index=False)
    print("Artists data saved to extracted_artists.csv")

if __name__ == '__main__':
    main()
