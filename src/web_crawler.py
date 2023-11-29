import requests
from bs4 import BeautifulSoup
import re

# initialize the data structure where to
# store the scraped data
faculties = []
visited_pages = set()

# initialize the list of discovered urls
# with the first page to visit
# urls = ["https://cs.illinois.edu/about/people/all-faculty"]
urls = ["https://cs.illinois.edu"]

# until all pages have been visited
while len(urls) != 0:
    # get the page to visit from the list
    current_url = urls.pop()
    
    # cant crawl page already seen
    if current_url in visited_pages:
        continue

    visited_pages.add(current_url)
    # crawling logic
    response = requests.get(current_url)
    soup = BeautifulSoup(response.content, "html.parser")

    link_elements = soup.select("a[href]")
    # if current_url == 'https://cs.illinois.edu/about/people/all-faculty':
    #     print("all-facult stuff: ", link_elements)
    
    for link_element in link_elements:
        url = link_element["href"]

        if '/about/people/all-faculty' in url:
            urls.append("https://cs.illinois.edu" + url)

        # if re.match(r"/about/people/all\-faculty/\w", url):
        #     urls.append("https://cs.illinois.edu" + url)
            
    # print(urls)

    # if current_url is product page
    faculty = {}
    faculty["url"] = current_url
    # TODO: data extraction HERE

    faculties.append(faculty)
    
print(faculties)


