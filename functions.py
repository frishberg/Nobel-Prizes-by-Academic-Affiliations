import requests
import time

exclude_list = [
    "/wiki/Bachelor_of_Arts",
    "/wiki/Bachelor_of_Science",
    "/wiki/Master_of_Arts",
    "/wiki/Master_of_Science",
    "/wiki/Doctor_of_Philosophy",
    "/wiki/Doctor_of_Medicine",
    "/wiki/Doctor_of_Laws",
    "/wiki/Master_of_Business_Administration",
    "/wiki/PhD",
]

json_data = {}

def scrape(url) :
    r = requests.get(url)
    return r.text

def find_all_links(s) :
    links = []
    while ("href=" in s) :
        s=s[s.index("href=")+6:]
        link = s[:s.index('"')]
        s=s[s.index('"'):]
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

#this method scrapes the wikipedia page of the given link and then tries to scrape the listings under Education and Institutions.  It's definitely not perfect but through my testing, it seems basically flawless.  Should work well enough so that the list is short enough so I can go through to verify manually
def scrape_alma_matters_and_institution(link) :
    alma_matters = [] #universities they attended
    institutions = [] #universities they worked at
    source = scrape(link)
    try :
        temp_source = source[source.index('Education</th>'):]
        temp_source = temp_source[:temp_source.index('</tr>')]
        while("href" in temp_source) :
            temp_source = temp_source[temp_source.index('href="')+6:]
            alma_matter = temp_source[:temp_source.index('"')]
            if ("/wiki/" in alma_matter and alma_matter not in exclude_list) :
                alma_matter = alma_matter
                alma_matters.append(alma_matter)
    except :
        print("No education found for " + link + " (education)")
    try :
        temp_source = source[source.index('Alma&#160;mater</th>'):]
        temp_source = temp_source[:temp_source.index('</tr>')]
        while("href" in temp_source) :
            temp_source = temp_source[temp_source.index('href="')+6:]
            alma_matter = temp_source[:temp_source.index('"')]
            if ("/wiki/" in alma_matter and alma_matter not in exclude_list) :
                alma_matter = alma_matter
                alma_matters.append(alma_matter)
    except :
        print("No education found for " + link + " (alma mater)")
    try :
        source = source[source.index('Institutions</th>'):]
        source = source[:source.index("</tr>")]
        while("href" in source) :
            source = source[source.index('href="')+6:]
            institution = source[:source.index('"')]
            if ("/wiki/" in institution and institution not in exclude_list) :
                institution = institution
                institutions.append(institution)
    except :
        print("No institutions found for " + link)
    return alma_matters, institutions

#generates data.json file, with a json of all the scraped data
def main() :
    #scrape_laureates() #retrieves all the wikipedia links of the laureates and saves them to "laureates.txt"
    f = open("laureates.txt", "r", encoding="utf-8")
    for link in f.readlines() :
        link=link.strip()
        cur_alma_matters, cur_institutions = scrape_alma_matters_and_institution(link)
        json_data[link] = {"alma_matters":cur_alma_matters, "institutions":cur_institutions}
    f.close()
    f = open("data.json", "w", encoding="utf-8")
    f.write(str(json_data))
    f.close()

main()