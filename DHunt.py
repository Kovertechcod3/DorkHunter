import requests
from bs4 import BeautifulSoup
import argparse
import sys


def search_emails(username, domain, dork):
    # Define the search query using the selected Google Dork
    search_query = f'site:{domain} {dork} "{username}"'

    # Send a request and retrieve the search results
    url = f'https://www.google.com/search?q={search_query}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Process the search results
    email_results = []
    search_results = soup.select('.r')  # Adjust the selector based on the structure of Google search results

    for result in search_results:
        link_element = result.select_one('a')
        if link_element:
            link = link_element['href']
            email = extract_email_from_link(link)
            if email:
                email_results.append(email)

    return email_results


def extract_email_from_link(link):
    # Extract the email from the link URL
    start_index = link.find('://') + 3
    end_index = link.find('/', start_index)
    if end_index == -1:
        end_index = len(link)
    email = link[start_index:end_index]
    if '@' in email:
        return email
    return None


def print_dorks():
    # Print the available Google Dorks for selection
    print("Available Google Dorks:")
    print("1. intext: - Searches for the username within the content of the page.")
    print("2. intitle: - Searches for the username within the title of the page.")
    print("3. inurl: - Searches for the username within the URL of the page.")


def main(username, domain, dork):
    # Search for emails
    emails = search_emails(username, domain, dork)

    if emails:
        print(f"Emails associated with '{username}' on '{domain}':")
        for email in emails:
            print(email)
    else:
        print(f"No emails found associated with '{username}' on '{domain}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for emails using Google Dorks.")
    parser.add_argument("username", type=str, help="Username to search for")
    parser.add_argument("domain", type=str, help="Domain to search within")
    parser.add_argument(
        "dork_choice",
        type=int,
        choices=[1, 2, 3],
        help="Select a Google Dork (1 for intext, 2 for intitle, 3 for inurl)",
    )
    args = parser.parse_args()

    dork_mapping = {
        1: "intext",
        2: "intitle",
        3: "inurl",
    }
    dork = dork_mapping[args.dork_choice]

    main(args.username, args.domain, dork)
