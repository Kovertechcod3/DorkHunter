# DorkHunter Tool

This tool allows you to search for email addresses associated with a specific username and domain using Google Dorks. It uses the BeautifulSoup library to parse the HTML of Google search results and extract email addresses from links.

## Requirements

- Python 3.x
- requests
- bs4 (BeautifulSoup)

## Usage

To use the tool, run the following command in your terminal:

```python
python dorkhunter.py [username] [domain] [dork_choice]
```

Replace `[username]` with the username you want to search for, `[domain]` with the domain you want to search within, and `[dork_choice]` with the number corresponding to the Google Dork you want to use (1 for intext, 2 for intitle, 3 for inurl).

For example:

```python
python dorkhunter.py johnsmith example.com 2
```
