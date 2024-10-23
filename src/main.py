import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Function to load the updated CSV
def load_labels_csv(filepath):
    return pd.read_csv(filepath, encoding='utf-8-sig')

# Function to scrape artist names dynamically based on tag path, class, and class tag
def extract_artist_names(url, tag_path=None, class_name=None, class_tag=None):
    try:
        # Set headers to mimic a browser
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        # Send a request to the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse the tag path (e.g., div>h3>a)
        tags = tag_path.split('>')
        current_elements = [soup]
        
        # Loop through each tag in the path
        for tag in tags:
            next_elements = []
            for element in current_elements:
                if tag == class_tag and class_name:  # Apply class only to the specified tag
                    next_elements.extend(element.find_all(tag, class_=class_name))
                else:
                    next_elements.extend(element.find_all(tag))
            current_elements = next_elements
        
        # Extract and return all artist names
        artist_names = [element.get_text().strip() for element in current_elements if element]
        
        # Debugging: Print the artist names for each label
        print(f"Extracted artist names for URL {url}: {artist_names}")
        
        return artist_names
    
    except Exception as e:
        print(f"Error while scraping {url}: {e}")
        return []

# Function to save artist names horizontally with labels as column headers
def save_to_csv(labels_artists, output_filepath):
    # Get the maximum number of artists for any label to pad columns correctly
    max_artists = max(len(artists) for artists in labels_artists.values())
    
    # Prepare rows for CSV (labels in the first row, followed by artists in the columns)
    rows = []
    
    # First row: labels as headers
    headers = list(labels_artists.keys())
    rows.append(headers)
    
    # For each row, we will add the corresponding artist under each label
    for i in range(max_artists):
        row = []
        for label in headers:
            # If there are enough artists for this label, append artist name; otherwise, append empty string
            if i < len(labels_artists[label]):
                row.append(labels_artists[label][i])
            else:
                row.append('')  # Pad with an empty string if there are fewer artists
        rows.append(row)
    
    # Write the rows to the CSV file
    with open(output_filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

# Main process
def main():
    # Load the CSV file containing the labels and URL info
    labels_df = load_labels_csv('data/Labels.csv')
    
    # Output CSV file
    output_filepath = 'data/Artists.csv'
    
    # Dictionary to store label and corresponding artists
    labels_artists = {}
    
    # Loop through each label and scrape artist names
    for _, row in labels_df.iterrows():
        label = row['Label Name']
        url = row['URL']
        tag_path = row['Tag Path']
        class_name = row['Class Name'] if pd.notna(row['Class Name']) else None
        class_tag = row['Class Tag'] if pd.notna(row['Class Tag']) else None
        
        # Extract artist names from the webpage
        artist_names = extract_artist_names(url, tag_path=tag_path, class_name=class_name, class_tag=class_tag)
        
        # Store artist names under their respective label
        if artist_names:
            labels_artists[label] = artist_names
    
    # Once all labels and artist names are collected, save to CSV
    if labels_artists:
        save_to_csv(labels_artists, output_filepath)

if __name__ == '__main__':
    main()
