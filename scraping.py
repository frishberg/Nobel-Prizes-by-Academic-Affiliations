import requests
import json
from unidecode import unidecode
import html
import urllib.parse
from bs4 import BeautifulSoup


exclude_list = [
    "/wiki/Bachelor_of_",
    "/wiki/Master_of_",
    "/wiki/Doctor_of_",
    "/wiki/Dr._",
    "/wiki/PhD",
    "/wiki/Habilitation",
    "/wiki/B.",
    "/wiki/M._S.",
    "/wiki/M.S.",
    "/wiki/M._A.",
    "/wiki/M.A.",
    "/wiki/M._Phil.",
    "/wiki/M.Phil.",
    "/wiki/M._D.",
    "/wiki/M.D.",
    "/wiki/Bachelor%27s_degree",
    "/wiki/NASA",
    "/wiki/NIST",
    "/wiki/BIRDEM",
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
                alma_matters.append(clean_up(alma_matter))
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
                alma_matters.append(clean_up(alma_matter))
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
                institutions.append(clean_up(institution))
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
                institutions.append(clean_up(institution))
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
    s = urllib.parse.quote(s, encoding='utf-8')
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

#goes through and looks for cases where schools are at the wrong link (ex. wiki/MIT & wiki/Massac... or wiki/Olin_Business_School vs wiki/Wash...)
def fix_mistakes() :
    #replacement section
    f = open("data.json", "r", encoding="utf-8")
    data = f.read()
    f.close()

    #edits
    data = data.replace("/wiki/MIT", "/wiki/Massachusetts_Institute_of_Technology")
    data = data.replace("/wiki/Caltech", "/wiki/California_Institute_of_Technology")
    data = data.replace("/wiki/NYU", "/wiki/New_York_University")
    data = data.replace('"/wiki/Harvard"\n', '"/wiki/Harvard_University"\n')
    data = data.replace("/wiki/University_of_Chicago_Booth_School_of_Business", "/wiki/University_of_Chicago")
    data = data.replace("/wiki/Booth_School_of_Business", "/wiki/University_of_Chicago")
    data = data.replace("/wiki/Stanford_University_School_of_Medicine", "/wiki/Stanford_University")
    data = data.replace("/wiki/Simon_Business_School", "/wiki/University_of_Rochester")
    data = data.replace("/wiki/Samuel_Curtis_Johnson_Graduate_School_of_Management", "/wiki/Cornell_University")
    data = data.replace("/wiki/Olin_Business_School", "/wiki/Washington_University_in_St._Louis")
    data = data.replace("/wiki/Perelman_School_of_Medicine_at_the_University_of_Pennsylvania", "/wiki/University_of_Pennsylvania")
    data = data.replace("/wiki/Columbia_Law_School", "/wiki/Columbia_University")
    data = data.replace("/wiki/New_York_University_School_of_Law", "/wiki/New_York_University")
    data = data.replace("/wiki/Case_Western_Reserve_University_School_of_Medicine", "/wiki/Case_Western_Reserve_University")
    data = data.replace("/wiki/Johns_Hopkins_School_of_Medicine", "/wiki/Johns_Hopkins_University")
    data = data.replace("/wiki/Washington_University_School_of_Medicine", "/wiki/Washington_University_in_St._Louis")
    data = data.replace("/wiki/Harvard_Medical_School", "/wiki/Harvard_University")
    data = data.replace("/wiki/New_York_University_School_of_Medicine", "/wiki/New_York_University")
    data = data.replace("/wiki/University_of_Pennsylvania_School_of_Medicine", "/wiki/University_of_Pennsylvania")
    data = data.replace("/wiki/Rady_School_of_Management", "/wiki/University_of_California,_San_Diego")
    data = data.replace("/wiki/New_York_University_Tandon_School_of_Engineering", "/wiki/New_York_University")
    data = data.replace("Robert_Wood_Johnson_Medical_School", "/wiki/Rutgers_University")
    data = data.replace("/wiki/Tulane_University_School_of_Medicine", "/wiki/Tulane_University")
    data = data.replace("/wiki/UCLA_School_of_Medicine", "/wiki/University_of_California,_Los_Angeles")
    data = data.replace("/wiki/Tufts_University_School_of_Medicine", "/wiki/Tufts_University")
    data = data.replace("/wiki/University_of_Massachusetts_Medical_School", "/wiki/University_of_Massachusetts")
    data = data.replace("/wiki/Harvard_School_of_Medicine", "/wiki/Harvard_University")
    data = data.replace("/wiki/Boston_University_School_of_Medicine", "/wiki/Boston_University")
    data = data.replace("/wiki/Harvard_Law_School", "/wiki/Harvard_University")
    data = data.replace("/wiki/Harvard_University_Law_School", "/wiki/Harvard_University")
    data = data.replace("/wiki/UNC_School_of_Medicine", "/wiki/University_of_North_Carolina_at_Chapel_Hill")
    data = data.replace("/wiki/Yale_School_of_Medicine", "/wiki/Yale_University")
    data = data.replace("/wiki/Stanford_University_School_of_Medicine", "/wiki/Stanford_University")
    data = data.replace("/wiki/Baylor_College_of_Medicine", "/wiki/Baylor_University")
    data = data.replace("/wiki/University_of_Texas_Southwestern_Medical_Center", "/wiki/University_of_Texas_at_Dallas")
    data = data.replace("/wiki/Weill_Cornell_Medicine", "/wiki/Cornell_University")
    data = data.replace("/wiki/Columbia_University_College_of_Physicians_and_Surgeons", "/wiki/Columbia_University")
    data = data.replace("/wiki/UCLA", "/wiki/University_of_California,_Los_Angeles")
    data = data.replace("/wiki/UC_Berkeley", "/wiki/University_of_California,_Berkeley")
    data = data.replace("/wiki/UC_San_Diego", "/wiki/University_of_California,_San_Diego")
    data = data.replace("/wiki/UC_Santa_Barbara", "/wiki/University_of_California,_Santa_Barbara")
    data = data.replace("/wiki/Gottingen_University", "/wiki/University_of_Gottingen")
    data = data.replace("/wiki/Georg_August_University_of_Gottingen", "/wiki/University_of_Gottingen")
    data = data.replace("/wiki/The_Rockefeller_University", "/wiki/Rockefeller_University")
    data = data.replace("/wiki/University_of_California_at_Berkeley", "/wiki/University_of_California,_Berkeley")
    data = data.replace("/wiki/University_of_Illinois_at_Urbana-Champaign", "/wiki/University_of_Illinois_Urbana-Champaign")
    data = data.replace("/wiki/University_of_Leiden", "/wiki/Leiden_University")
    data = data.replace("/wiki/University_of_Wisconsin,_Madison", "/wiki/University_of_Wisconsin-Madison")
    data = data.replace("/wiki/University_of_Colorado_at_Boulder", "/wiki/University_of_Colorado_Boulder")
    data = data.replace("/wiki/King's_College,_London", "/wiki/King's_College_London")
    #edits

    data = data.replace("%27", "'")
    data = data.replace("%2C", ",")
    data = data.replace("%252C", ",")
    data = data.replace("%2527", "'")

    f = open("data.json", "w", encoding="utf-8")
    f.write(data)
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



#scrape_laureates() #generates laureates.txt
#main() #generates data.json using the laureates.txt file
fix_mistakes()
generate_list_of_universities() #generates universities.txt