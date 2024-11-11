import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from exclude_terms import exclude_terms, exclude_patterns

# Function to load the updated CSV
def load_labels_csv(filepath):
    return pd.read_csv(filepath, encoding='utf-8-sig')

# Function to scrape content specifically from <a> and <h3> tags
def extract_content(url):
    try:
        # Set headers to mimic a browser
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Define tags to check for content extraction
        content_tags = ['a', 'h3', 'h2']
        
        content_list = []
        
        # Extract text from specified tags and filter out unwanted terms
        for tag in content_tags:
            for element in soup.find_all(tag):
                text = element.get_text().strip()
                # Preserve numeric names by allowing them if not filtered out
                if (text 
                    and not any(term in text for term in exclude_terms)
                    and not any(pattern in text for pattern in exclude_patterns)
                    and len(text) > 1):
                    content_list.append(text)

        # Debugging: Print the extracted content for verification
        print(f"Extracted content for URL {url}: {content_list}")
        return content_list

    except Exception as e:
        print(f"Error while scraping {url}: {e}")
        return []

# Function to save the extracted content to a CSV
def save_to_csv(labels_content, output_filepath):
    # Prepare rows for CSV with labels as headers
    rows = []
    headers = list(labels_content.keys())
    rows.append(headers)

    # Determine the maximum number of items under any label to pad rows correctly
    max_content_length = max(len(content) for content in labels_content.values())

    # Build rows of content, with each label's content aligned vertically
    for i in range(max_content_length):
        row = []
        for label in headers:
            row.append(labels_content[label][i] if i < len(labels_content[label]) else "")
        rows.append(row)

    # Write rows to the CSV file with utf-8-sig encoding
    with open(output_filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

# Function to remove duplicates from content list
def remove_duplicates(content_list):
    return list(dict.fromkeys(content_list))

# Main process
def main():
    # Load the CSV file containing the labels and URL info
    labels_df = load_labels_csv('data/labels.csv')
    
    # Output CSV file
    output_filepath = 'data/content_list80.csv'  # Change the output filename here for flexibility
    
    # Dictionary to store label and corresponding content
    labels_content = {}
    
    # Loop through each label and scrape content
    for _, row in labels_df.iterrows():
        label = row['Label Name']
        url = row['URL']
        
        # Extract content from the webpage
        content_list = extract_content(url)

        # Remove duplicates from the content list
        content_list = remove_duplicates(content_list)
        
        # Store content under its respective label
        if content_list:
            labels_content[label] = content_list
    
    # Once all labels and content are collected, save to CSV
    if labels_content:
        save_to_csv(labels_content, output_filepath)

if __name__ == '__main__':
    main()
