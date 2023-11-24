'''搜索小说

>>> import novel
>>> novel.search_novel('牧神记')
'''

import requests
from bs4 import BeautifulSoup


# Function to check if the novel has been updated
def search_novel(novel_name: str) -> str:
    # Replace spaces with dashes for URL formatting
    formatted_novel_name = novel_name.replace(' ', '-')
    # Construct the URL to check for updates
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '}
    url = f'https://www.xbiquge.la/modules/article/waps.php?searchkey={formatted_novel_name}'
    # Send a request to the website
    response = requests.get(url, headers=headers)
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the table with the novel information
    table = soup.find('table')
    if table:
        # Find all rows in the table
        rows = table.find_all('tr')
        # Check if there are any rows
        return str(rows[:5])
    return 'No results found.'

__all__ = ['search_novel']
