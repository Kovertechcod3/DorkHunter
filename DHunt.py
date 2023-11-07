import requests
from bs4 import BeautifulSoup
import argparse
import sys


def search_usernames(email, domain, dork):
    # Define the search query using the selected Google Dork
    search_query = f'site:{domain} {dork} "{email}"'

    # Send a request and retrieve the search results
    url = f'https://www.google.com/search?q={search_query}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Process the search results
    username_results = []
    search_results = soup.select('.r')  # Adjust the selector based on the structure of Google search results

    for result in search_results:
        link_element = result.select_one('a')
        if link_element:
            link = link_element['href']
            username = extract_username_from_link(link)
            if username:
                username_results.append(username)

    return username_results


def extract_username_from_link(link):
    # Extract the username from the link URL
    start_index = link.find('://') + 3
    end_index = link.find('/', start_index)
    if end_index == -1:
        end_index = len(link)
    username = link[start_index:end_index]
    if '@' not in username:
        return username
    return None


def print_dorks():
    # Print the available Google Dorks for selection
    print("Available Google Dorks:")
    print("1. intext: - Searches for the username within the content of the page.")
    print("2. intitle: - Searches for the username within the title of the page.")
    print("3. inurl: - Searches for the username within the URL of the page.")


def main(email, domain, dork):
    # Search for usernames
    usernames = search_usernames(email, domain, dork)

    if usernames:
        print(f"Usernames associated with '{email}' on '{domain}':")
        for username in usernames:
            print(username)
    else:
        print(f"No usernames found associated with '{email}' on '{domain}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for usernames using Google Dorks.")
    parser.add_argument("email", type=str, help="Email address to search for")
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

    main(args.email, args.domain, dork)
