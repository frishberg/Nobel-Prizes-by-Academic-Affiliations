import requests
import json
from unidecode import unidecode
import urllib.parse

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
def scrape_wiki_data(link) :
    alma_matters = [] #universities they attended
    institutions = [] #universities they worked at
    category = "" #physics, chemistry, etc.
    year = "" #year they won the nobel prize

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
    
    #getting the category and year
    temp_source = source[source.index('Awards'):]
    if ("/wiki/Nobel_Prize_in_" in temp_source) : #chemistry, physics, literature, medicine
        temp_source = temp_source[temp_source.index("/wiki/Nobel_Prize_in_")+21:]
        print(temp_source)
        category = temp_source[:temp_source.index('"')]
        temp_source = temp_source[temp_source.index('(')+1:]
        try :
            year = int(temp_source[:temp_source.index(')')])
        except :
            print("No prize year found for " + link)
    elif ("/wiki/Nobel_Memorial_Prize_in_Economic_Sciences" in temp_source) : #economics
        category = "Economics"
        temp_source = temp_source[temp_source.index("/wiki/Nobel_Memorial_Prize_in_Economic_Sciences")+45:]
        temp_source = temp_source[temp_source.index('(')+1:]
        try :
            year = int(temp_source[:temp_source.index(')')])
        except :
            print("No prize year found for " + link)
    elif ("/wiki/Nobel_Peace_Prize" in temp_source) : #peace
        category = "Peace"
        temp_source = temp_source[temp_source.index("/wiki/Nobel_Peace_Prize")+23:]
        temp_source = temp_source[temp_source.index('(')+1:]
        try :
            year = int(temp_source[:temp_source.index(')')])
        except :
            print("No prize year found for " + link)
    else :
        raise Exception("Category not found for " + link)
    return alma_matters, institutions, category, year

#takes in a name, like Wilhelm R%C3%B6ntgen and returns Wilhelm Rontgen.  Gets rid of annoying unicode characters
def clean_up(s) :
    s = urllib.parse.unquote(s, encoding='utf-8')
    s = unidecode(s)
    return urllib.parse.quote(s, encoding='utf-8')

#generates data.json file, with a json of all the scraped data
def main() :
    #scrape_laureates() #retrieves all the wikipedia links of the laureates and saves them to "laureates.txt"
    f = open("laureates.txt", "r", encoding="utf-8")
    for link in f.readlines() :
        print(link)
        link = "https://en.wikipedia.org" + link.strip()
        name = clean_up(link[link.index("/wiki/")+6:]).replace("_", " ") #getting rid of stuff like H%C3%A4 and replacing _ with spaces
        cur_alma_matters, cur_institutions, category, year = scrape_wiki_data(link)
        json_data[name] = {}
        json_data[name]["link"] = link
        json_data[name]["category"] = category
        json_data[name]["year"] = year
        json_data[name]["alma_matters"] = cur_alma_matters
        json_data[name]["institutions"] = cur_institutions
    f.close()
    f = open("data.json", "w", encoding="utf-8")
    f.write(json.dumps(json_data))
    f.close()

#main()
print(scrape_wiki_data("https://en.wikipedia.org/wiki/Philip_H._Dybvig"))