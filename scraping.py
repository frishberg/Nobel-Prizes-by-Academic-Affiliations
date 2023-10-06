import requests
import time
import json

exclude_list = [
    "/wiki/Bachelor_of_",
    "/wiki/Master_of_",
    "/wiki/Doctor_of_",
    "/wiki/PhD",
    "/wiki/Habilitation"
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

#makes sure that none of the exclusion terms are in the link (ex. bachelor)
def non_exclude_list(link) :
    for exclude in exclude_list :
        if exclude in link :
            return False
    return True

#there are some small things that cause issues, like if the Alma matter header is a link instead of p.  This method fixes those issues
def special_exceptions(source) :
    source = source.replace('<a href="/wiki/Alma_mater" title="Alma mater">Alma mater</a>', 'Alma&#160;mater</th>')
    return source

#this method scrapes the wikipedia page of the given link and then tries to scrape the listings under Education and Institutions.  It's definitely not perfect but through my testing, it seems basically flawless.  Should work well enough so that the list is short enough so I can go through to verify manually
def scrape_alma_matters_and_institution(link) :
    alma_matters = [] #universities they attended
    institutions = [] #universities they worked at
    source = special_exceptions(scrape(link))
    try :
        temp_source = source[source.index('Education</th>'):]
        temp_source = temp_source[:temp_source.index('</tr>')]
        while("href" in temp_source) :
            temp_source = temp_source[temp_source.index('href="')+6:]
            alma_matter = temp_source[:temp_source.index('"')]
            if ("/wiki/" in alma_matter and non_exclude_list(alma_matter)) :
                alma_matter = alma_matter
                alma_matters.append(alma_matter)
    except :
        pass
    try :
        temp_source = source[source.index('Alma&#160;mater</th>'):]
        temp_source = temp_source[:temp_source.index('</tr>')]
        while("href" in temp_source) :
            temp_source = temp_source[temp_source.index('href="')+6:]
            alma_matter = temp_source[:temp_source.index('"')]
            if ("/wiki/" in alma_matter and non_exclude_list(alma_matter)) :
                alma_matter = alma_matter
                alma_matters.append(alma_matter)
    except :
        pass
    if (len(alma_matters) == 0) :
        print("No alma matters found for " + link)
    try :
        temp_source = source[source.index('Institutions</th>'):]
        temp_source = temp_source[:temp_source.index("</tr>")]
        while("href" in temp_source) :
            temp_source = temp_source[temp_source.index('href="')+6:]
            institution = temp_source[:temp_source.index('"')]
            if ("/wiki/" in institution and non_exclude_list(institution)) :
                institution = institution
                institutions.append(institution)
    except :
        pass
    try :
        temp_source = source[source.index('Institution</th>'):]
        temp_source = temp_source[:temp_source.index("</tr>")]
        while("href" in temp_source) :
            temp_source = temp_source[temp_source.index('href="')+6:]
            institution = temp_source[:temp_source.index('"')]
            if ("/wiki/" in institution and non_exclude_list(institution)) :
                institution = institution
                institutions.append(institution)
    except :
        pass
    if (len(institutions) == 0) :
        print("No institutions found for " + link)
    return alma_matters, institutions

#generates data.json file, with a json of all the scraped data
def main() :
    #scrape_laureates() #retrieves all the wikipedia links of the laureates and saves them to "laureates.txt"
    f = open("laureates.txt", "r", encoding="utf-8")
    for link in f.readlines() :
        link = "https://en.wikipedia.org" + link.strip()
        cur_alma_matters, cur_institutions = scrape_alma_matters_and_institution(link)
        json_data[link] = {}
        json_data[link]["alma_matters"] = cur_alma_matters
        json_data[link]["institutions"] = cur_institutions
    f.close()
    f = open("data.json", "w", encoding="utf-8")
    f.write(json.dumps(json_data))
    f.close()

main()
#print(scrape_alma_matters_and_institution("https://en.wikipedia.org/wiki/Philip_Noel-Baker"))