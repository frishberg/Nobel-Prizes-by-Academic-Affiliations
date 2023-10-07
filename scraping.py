import requests
import json
from unidecode import unidecode
import urllib.parse
from bs4 import BeautifulSoup

exclude_list = [
    "/wiki/Bachelor_of_",
    "/wiki/Master_of_",
    "/wiki/Doctor_of_",
    "/wiki/PhD",
    "/wiki/Habilitation",
    "/wiki/B._S.",
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
    categories = ["Physics", "Chemistry", "Medicine", "Literature", "Peace", "Economics"]
    s = ""
    url = "https://en.wikipedia.org/wiki/List_of_Nobel_laureates#Laureates"
    source = scrape(url)
    source = source[source.index('<tbody>'):]
    source = source[:source.index('</tbody>')]
    soup = BeautifulSoup(source, 'html.parser')
    rows = soup.find_all('tr')
    for row in rows :
        try :
            year = str(row.find('td'))
            year = year[year.index('>')+1:]
            year = int(year[:year.index('<')-1])
            n = -1 #keeping track of the column number in this row so that category can be determined (ex. 0 is physics).  It also has to start at -1 because the first column is the year

            for square in row.find_all('td') :
                category = categories[n]
                laureates = square.find_all('a')
                for laureate in laureates :
                    link = laureate.get('href')
                    if ("#" not in link) : #avoiding links like #cite_note-15
                        s+=link + " (" + category + " " + str(year) + ")\n" #ex. /wiki/Wilhelm_R%C3%B6ntgen (Physics 1901)
                n+=1
        except :
            pass
        
        f = open("laureates.txt", "w", encoding="utf-8")
        f.write(s)
        f.close()

    
    f = open("laureates.txt", "w", encoding="utf-8")
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
    
    return alma_matters, institutions

#takes in a name, like Wilhelm R%C3%B6ntgen and returns Wilhelm Rontgen.  Gets rid of annoying unicode characters
def clean_up(s) :
    s = urllib.parse.unquote(s, encoding='utf-8')
    s = unidecode(s)
    return urllib.parse.quote(s, encoding='utf-8')

def generate_list_of_universities() :
    f = open("data.json", "r", encoding="utf-8")
    data = json.loads(f.read())
    f.close()
    universities = []
    for name in data :
        for alma_matter in data[name]["alma_matters"] :
            if alma_matter not in universities :
                universities.append(alma_matter)
        for institution in data[name]["institutions"] :
            if institution not in universities :
                universities.append(institution)
    f = open("universities.txt", "w", encoding="utf-8")
    for university in universities :
        f.write('"' + university + '",\n')
    f.close()

#generates data.json file, with a json of all the scraped data
def main() :
    #scrape_laureates() #retrieves all the wikipedia links of the laureates and saves them to "laureates.txt"
    f = open("laureates.txt", "r", encoding="utf-8")
    for link in f.readlines() :
        category, year = link[link.rindex("(")+1:link.rindex(")")].split(" ")
        link = link[:link.rindex("(")].strip() #getting rid of the category and year (ex. /wiki/Wilhelm_R%C3%B6ntgen (Chemistry 1901) -> /wiki/Wilhelm_R%C3%B6ntgen)
        link = "https://en.wikipedia.org" + link
        name = clean_up(link[link.index("/wiki/")+6:]).replace("_", " ") #getting rid of stuff like H%C3%A4 and replacing _ with spaces
        cur_alma_matters, cur_institutions = scrape_wiki_data(link)
        json_data[name] = {}
        json_data[name]["link"] = link
        json_data[name]["category"] = category
        json_data[name]["year"] = int(year)
        json_data[name]["alma_matters"] = cur_alma_matters
        json_data[name]["institutions"] = cur_institutions
    f.close()
    f = open("data.json", "w", encoding="utf-8")
    f.write(json.dumps(json_data))
    f.close()



#main()
#scrape_laureates()
generate_list_of_universities()