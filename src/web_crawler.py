import requests
from bs4 import BeautifulSoup
import re

# initialize the data structure where to
# store the scraped data
faculties = []
visited_pages = set()

# initialize the list of discovered urls
# with the first page to visit
urls = ["https://cs.illinois.edu/about/people"]
#urls = ["https://cs.illinois.edu"]

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
    
    for link_element in link_elements:
        url = link_element["href"]

        if '/about/people/all-faculty/department-faculty' in url and "https://cs.illinois.edu" + url not in visited_pages:
            urls.append("https://cs.illinois.edu" + url)
        
        if '/about/people/department-faculty' in url and "https://cs.illinois.edu" + url not in visited_pages:
            urls.append("https://cs.illinois.edu" + url)
            
    faculty = {}
    faculty["url"] = current_url
    faculty["name"] = soup.find("figcaption").text.strip()
    faculty["research_areas"] = []
    faculty["research_interests"] = []
    faculty["education"] = []
    for ra in soup.find("div", attrs={"class": "extProfileAREA"}).find_all("li"):
        faculty["research_areas"].append(ra.text)
    ri_flag = False
    ed_flag = False
    for element in soup.find("div", attrs={"class": "directory-profile"}).find_all():
        if element.text.lower().strip() == "education":
            ed_flag = True
            continue
        if element.text == "Research Interests":
            ri_flag = True
            ed_flag = False
            continue
        if element.text == "Research Areas":
            ri_flag = False
        if ed_flag:
            faculty["education"].append(element.text.replace("\n", " ").strip())

        if ri_flag and "\n" not in element.text:
            faculty["research_interests"] += [i.strip() for i in element.text.split(',')]

    faculties.append(faculty)
    
#print(faculties)

