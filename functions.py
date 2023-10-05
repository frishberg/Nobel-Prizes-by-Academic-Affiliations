import requests

def scrape(url) :
    r = requests.get(url)
    return r.text

def find_all_links(s) :
    links = []
    while ("href=" in s) :
        s=s[s.index("href=")+6:]
        link = s[:s.index('"')]
        s=s[s.index('"'):]
        if ("/wiki/" in link) :
            link = "https://en.wikipedia.org" + link
        if link not in links and "#" not in link :
            links.append(link)
    return links

def scrape_laureates() :
    f = open("laureates.txt", "w", encoding="utf-8")
    s = ""
    url = "https://en.wikipedia.org/wiki/List_of_Nobel_laureates#Laureates"
    source = scrape(url)
    source = source[source.index('<td align="center">1901'):]
    source = source[:source.index('<th width="16%"><a href="/wiki/List_of_Nobel_laureates_in_Physics" title="List of Nobel laureates in Physics">Physics</a>')]
    links = find_all_links(source)
    for link in links :
        s += link + "\n"
    f.write(s)
    f.close()

def scrape_alma_matters_and_institution(link) :
    source = scrape(link)
    f = open("output.txt", "w", encoding="utf-8")
    f.write(source)
    f.close()

#scrape_laureates() #retrieves all the wikipedia links of the laureates and saves them to "laureates.txt"
alma_matters = []
alma_matters_frequency = []
institutions = []
institutions_frequency = []
scrape_alma_matters_and_institution("https://en.wikipedia.org/wiki/Albert_Einstein")