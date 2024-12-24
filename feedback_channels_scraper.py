
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

# Function to scrape feedback channels from a URL
def scrape_feedback_channels(url):
    try:
        response = requests.get(f"http://{url}", timeout=10)  # Adding http:// to avoid issues with incomplete URLs
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        feedback_channels = {
            "Email": 0,
            "Feedback Form": 0,
            "Social Media": 0,
            "Discussion Forum": 0,
            "Like/Rate/Fav": 0
        }

        # 1. Detect Email Addresses
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        if email_pattern.search(response.text):
            feedback_channels["Email"] = 1

        # 2. Detect Feedback Forms
        forms = soup.find_all('form')
        for form in forms:
            if any(keyword in form.get_text().lower() for keyword in ['feedback', 'contact']):
                feedback_channels["Feedback Form"] = 1
                break

        # 3. Detect Social Media Links
        social_media_domains = ['twitter.com', 'facebook.com', 'linkedin.com', 'instagram.com']
        links = soup.find_all('a', href=True)
        for link in links:
            if any(domain in link['href'] for domain in social_media_domains):
                feedback_channels["Social Media"] = 1
                break

        # 4. Detect Discussion Forums
        for link in links:
            if any(keyword in link['href'].lower() for keyword in ['forum', 'discussion', 'community']):
                feedback_channels["Discussion Forum"] = 1
                break

        # 5. Detect Like/Rate/Fav Buttons
        buttons = soup.find_all(['button', 'a'])
        for button in buttons:
            if any(keyword in button.get_text().lower() for keyword in ['like', 'rate', 'favorite']):
                feedback_channels["Like/Rate/Fav"] = 1
                break

        return feedback_channels

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

# Main script to read URLs from Excel and scrape information
def main():
    # Load Excel file
    file_path = "open_data_portals.xlsx"  # Replace with the path to your Excel file
    df = pd.read_excel(file_path)

    # Create a results list
    results = []

    for url in df['Open Data Portal URL']:
        print(f"Scraping {url}...")
        channels = scrape_feedback_channels(url)
        if channels:
            total_channels = sum(channels.values())  # Calculate the total feedback channels found
            results.append({
                "URL": url,
                "Email": channels["Email"],
                "Feedback Form": channels["Feedback Form"],
                "Social Media": channels["Social Media"],
                "Discussion Forum": channels["Discussion Forum"],
                "Like/Rate/Fav": channels["Like/Rate/Fav"],
                "Total Feedback Channels": total_channels
            })

    # Save the results to a new Excel file
    results_df = pd.DataFrame(results)
    results_df.to_excel("feedback_channels_summary.xlsx", index=False)
    print("Scraping complete! Results saved to 'feedback_channels_summary.xlsx'.")

if __name__ == "__main__":
    main()
