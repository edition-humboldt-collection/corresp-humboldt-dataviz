from nested_lookup import nested_lookup
import pandas as pd
import IPython
from IPython.display import display, clear_output
from ipywidgets import HTML, Output, HBox
from ipyleaflet import Map, Marker, Popup
import matplotlib.pyplot as plt


from .search_dynamic import show_webpage,btn_new_search
from .prepare_data import getJSON, avoidTupleInList, getYears
from .widgets import createDropdown, createButton, createCheckBox

data = getJSON('data/records.json')
out = Output()

def show_map(data: list, by : str, first: bool):
    """
    Show places (contributor or coverage place) on a map.
    
    :param data: List of letters
    :param by: Which points should appear on the map? Possibility : coverage_location or contributor_location
    :param first: Set False if you use it recursively
    """
    m = Map(
            center=(35.52437, -30.41053),
            zoom=2,
            close_popup_on_click=False
            )
    
    cities = {}
    marker = None

    for i in data:
            try :
                if i[by]["address"] not in cities:
                    city = i[by]["address"]
                    cities[city] = {}
                    cities[city]["message"] = "<b>"+ i["date"] + " </b> " + i["title"] + "<br><i>"+ i["contributor"] +"</i> <br> <a href=\""+ i["identifier"][1] + "\" target=\"_blank\">online</a> <hr>"
                    cities[city]["coordinates"] = [i[by]["coordinates"][1], i[by]["coordinates"][0]]
                    
                elif i[by]["address"] in cities:
                    city = i[by]["address"]
                    cities[city]["message"] = cities[city]["message"] + "<b>"+ i["date"] + " </b> " + i["title"] + "<br><i>"+ i["contributor"]  + "</i><br> <a href=\""+ i["identifier"][1] + "\" target=\"_blank\">online</a> <hr>"
            except : pass
    for i in cities.keys():
            try :
                message = HTML()
                if cities[i]["message"].count("<hr>") <3 :
                    message.value = cities[i]["message"]
                else : 
                    message.value = str(cities[i]["message"].count("<hr>")) + " letters. There are too many results to show them all here."
                message.description = i.upper()
                marker = Marker(location=(cities[i]["coordinates"][0], cities[i]["coordinates"][1]))
                m.add_layer(marker)
                marker.popup = message
            except: pass

    if marker == None and first == True :
        show_map(data, "contributor_location", False)
    elif marker == None and first == False:
        print("An error has been encountered, the map cannot be displayed. We propose to have access to the results in a table format.")
        display(pd.DataFrame(pd.json_normalize(data)))
    else:
        display(m)


def an_change(change):
    if change['new'] == True :
        results = []
        for i in data:
            try :
                if 'Humboldt, Alexander' in i["subject"]:
                    results.append(i)
            except : 
                continue

        clear_output()
        an = createCheckBox("an AvH", True)
        von = createCheckBox("von AvH", False)

        display(HBox([an, von]))
        an.observe(an_change)
        von.observe(von_change)

        searching_by = ['Sender letters','Date']
        display(HBox([mapsearch(results, searching_by, True), btn_new_search()]))

    elif change['new'] == False:
        both_uncheck()


def von_change(change):
    if change['new'] == True :
        results = []
        for i in data:
            try :
                if 'Humboldt, Alexander' in i["creator"]:
                    results.append(i)
            except : 
                continue

        clear_output()
        an = createCheckBox("an AvH", False)
        von = createCheckBox("von AvH", True)
        display(HBox([an, von]))
        an.observe(an_change)
        von.observe(von_change)

        searching_by = ['Recipients letters','Date']
        display(HBox([mapsearch(results, searching_by, True), btn_new_search()]))

    elif change['new'] == False:
        both_uncheck()

def both_uncheck():
    clear_output()
    an = createCheckBox("an AvH", False)
    von = createCheckBox("von AvH", False)

    display(HBox([an, von]))

    an.observe(an_change)
    von.observe(von_change)
    show_map(data, "coverage_location", True)


def date_change(change): 
    """
    Handle if a date is selected in a dropdown menu.
    :param change:
    """
    if change['type'] == 'change' and change['name'] == 'value':
        date = change['new']
        results = []

        for i in data:
            try : 
                if date in i["date"]:
                    results.append(i)
            except: pass
        show_map(results, "coverage_location", True)

    if date == False:
        show_map(data, "coverage_location", True)


def by_date(data:dict):
    """
    Create a dropdown menu containing years of a given letter`s dict.
    :param data: dict of letter
    :rtype: widget
    :return: dropdown
    """
    years = getYears(avoidTupleInList(nested_lookup('date', data)))
    dropdown = createDropdown('', years)
    dropdown.observe(date_change)
    return dropdown 


def is_male_name(name:str):
    """
    Check if the given name is a male name.
    :param name: str
    :rtype: bool
    :return: True or False
    """
    male_name = ['Chr.', 'Jean-Baptiste', 'Heymann', 'Étienne', 'Whitelaw', 'Balduin', 'Edme', 'Hipolit', 'Moriz', 'Modest', 'Alire', 'Christ...', 'Dimitrij', 'Francois', 'Elte', 'Aylmer' ]
    for i in male_name:
        if name == i:
            return True
    return False


def mapsearch(data, search_possibilities, flag : bool):
    """
    Recursive algorithm with allows 
    a dynamic search with a map visualisation of results.
    
    :param data: list
    :param search_possibilities: list
    :param flag: bool
    """
    search_by = search_possibilities
    search_dropdown = createDropdown('Search by', search_by)
    new = flag
    
    def show_results(results):
        if len(results) <10:
            show_map(results, "coverage_location", True)
        else : 
            mapsearch(results, search_by, False)


    def change_creators(change):
        if change['type'] == 'change' and change['name'] == 'value':
            sender = change['new']
            results = []
            for r in data:
                try :
                    if r['creator'] == sender:
                        results.append(r)
                except : 
                    continue
            search_by.remove('Sender letters')
            show_map(results, "coverage_location", True)

    def change_recipients(change):
        if change['type'] == 'change' and change['name'] == 'value':
            recipients = change['new']
            results = []
            for r in data:
                try :
                    if r['subject'] == recipients:
                        results.append(r)
                except : 
                    continue
            search_by.remove('Recipients letters')
            show_results(results)

    def change_date(change):
        if change['type'] == 'change' and change['name'] == 'value':
            date = change['new']
            results = []
            for r in data:
                try :
                    if date in r['date']:
                        results.append(r)
                except : 
                    continue
            search_by.remove('Date')
            show_results(results)

    def no_element_for_dropdown(data, searching_by, element):
        search_by.remove(element)
        print('There is no {0} registered for these data.'.format(element.lower()))
        mapsearch(data, search_by, False)

    def change_search(change): 
        if change['type'] == 'change' and change['name'] == 'value':
            if change['new'] == 'Sender letters' and change['type'] == 'change':
                creators = avoidTupleInList(nested_lookup('creator', data))
                if len(creators) == 0:
                    return no_element_for_dropdown(data, search_by, change['new'] )
                else :
                    dropdown = createDropdown('Senders', creators)
                    dropdown.observe(change_creators) 
            elif change['new'] == 'Recipients letters' and change['type'] == 'change':
                recipients = avoidTupleInList(nested_lookup('subject', data))
                if len(recipients) == 0:
                    return no_element_for_dropdown(data, search_by, change['new'] )
                else :
                    dropdown = createDropdown('Recipients', recipients)
                    dropdown.observe(change_recipients)
            elif change['new'] == 'Date' and change['type'] == 'change':
                years = getYears(avoidTupleInList(nested_lookup('date', data)))
                if len(years) == 0:
                    return no_element_for_dropdown(data, search_by, change['new'] )
                else :
                    dropdown = createDropdown('Dates', years)
                    dropdown.observe(change_date)
            display(dropdown)
    
    search_dropdown.observe(change_search)
    if flag == True:
        return search_dropdown
    else :
        return display(search_dropdown)


def person_change(change): 
    """
    Handle if a person was selected in the corresponding dropdown menu
    and show a histogramm of the correspondence between the selected person
    and Alexander von Humboldt.
    :param change: 
    """
    if change['type'] == 'change' and change['name'] == 'value':
        person = change['new']
        results = []
        # get the corresponding letters
        for i in data:
            try : 
                if person in i["creator"] or person in i["subject"]:
                    results.append(i)
            except: pass
        
        # from corresponding letters, get and transform the data to build the histogramm
        liste = []
        for i in results:
            try :
                if int(i['date'][:4]) <1859:
                    liste.append((int(i['date'][:4]), int(1)))
            except:pass
            
            
        # create the histogramm
        title = 'Correspondence between AvH(1769-1859) und ' + person
        x_coords = [coord[0] for coord in liste]
        y_coords = [coord[1] for coord in liste]
        fig= plt.figure(figsize=(10,5))
        plt.hist(x_coords, bins=30)
        fig.suptitle(title, fontsize=12)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Number of letters', fontsize=12)
        plt.show()


def by_person(data:dict):
    """
    Creates a dropdown menu of all people 
    who have received and/or sent at least one letter 
    for which a date is recorded
    :param data: dict
    :return: dropdown menu
    :rtype: widget
    """
    # Get the letters which have a recorded date
    with_date= []
    for i in data:
        try:
            if bool(i['date']) == True:
                with_date.append(i)
        except:pass
        
    # Get all people who received or sent a letter    
    creators = avoidTupleInList(nested_lookup('creator', with_date))
    subjects = avoidTupleInList(nested_lookup('subject', with_date))
    people = []
    
    # Delete Humboldt from creators' and subjects' lists
    for i in creators:
        if '[' in i :
            i = i.split(' [vermutlich]')[0]
        if 'Humboldt' not in i:
            people.append(i)
    for i in subjects:
        if 'Humboldt' not in i and i not in people:
            people.append(i)

    #Create dropdown Menu
    dropdown = createDropdown('', people)
    dropdown.observe(person_change)
    return dropdown 


def age_distribution() :
    years_an = {}
    years_von = {}
    
    liste_an=[]
    liste_von=[]
    
    # Letter to Humboldt
    for i in data :
        try :
            if i["date"] and "Humboldt" not in i["creator"] and type(i["creator"]) != list :
                if i["date"][:4] not in years_an:
                    years_an[i["date"][:4]] = []
                years_an[i["date"][:4]].append(int(i["date"][:4]) - int(i["creator"].split("(")[1].split("-")[0][:4]))
        except: pass 

    # Letter by Humboldt     
    for i in data :
        try :
            if i["date"] and "Humboldt" not in i["subject"] and type(i["subject"]) != list :
                if i["date"][:4] not in years_von:
                    years_von[i["date"][:4]] = []
                years_von[i["date"][:4]].append(int(i["date"][:4]) - int(i["subject"].split("(")[1].split("-")[0][:4]))
        except: pass 

    for element in years_an.keys():
        try :
            if (float(element)<1859):
                for element1 in years_an[element]: 
                    if (float(element1)>0):
                        liste_an.append((float(element), float(element1)))
        except : pass
                
    for element in years_von.keys():
        try :
            if (float(element)<1859):
                for element1 in years_von[element]: 
                    if (float(element1)>0):
                        liste_von.append((float(element), float(element1)))
        except : pass

    x_coords = [coord[0] for coord in liste_an]
    y_coords = [coord[1] for coord in liste_an]
    fig= plt.figure(figsize=(10,8))
    plt.hist2d(x_coords, y_coords, bins=(40, 40), cmap=plt.cm.Reds)
    fig.suptitle('Letters to AvH: age distribution of senders', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Age of the correspondence partner', fontsize=12)
    plt.colorbar()
    an_plt = plt.show()

    von_x_coords = [coord[0] for coord in liste_von]
    von_y_coords = [coord[1] for coord in liste_von]
    fig= plt.figure(figsize=(10,8))
    plt.hist2d(von_x_coords, von_y_coords, bins=(40, 40), cmap=plt.cm.Reds)
    fig.suptitle('Letters by AvH: age distribution of addressees', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Age of the correspondence partner', fontsize=12)
    plt.colorbar()
    von_plt = plt.show()

