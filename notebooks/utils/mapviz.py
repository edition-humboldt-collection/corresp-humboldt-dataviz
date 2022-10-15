import pandas as pd
import numpy
import random
import IPython
from IPython.display import display, clear_output
from ipywidgets import HTML, Output, HBox
from ipyleaflet import Map, Marker, Popup, CircleMarker
import matplotlib.pyplot as plt

from .nestedlookup import *
from .search_dynamic import show_webpage,btn_new_search
from .prepare_data import getJSON, avoidTupleInList, getYears, getHumboldtYears
from .widgets import createDropdown, createButton, createCheckBox

data = getJSON('data/records.json')
out = Output()


def create_histogramm(data, person):
    """
    Create a histogramm of the exchange of letters
    between AvH and a selected person during the time.
    :param data: List of letters
    :param person: Selected person 
    """
    title = 'Correspondence between AvH(1769-1859) und ' + person
    x_coords = [coord[0] for coord in data]
    fig= plt.figure(figsize=(10,5))
    plt.hist(x_coords, bins=30)
    fig.suptitle(title, fontsize=12)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of letters', fontsize=12)
    return plt

def show_map(data: list, by : str, first: bool):
    """
    Show places (contributor or coverage place) on a map.
    :param data: List of letters
    :param by: Which points should appear on the map? Possibility : coverage_location or contributor_location
    :param first: Set False if you use it recursively
    """
    cities = {}
    marker = None
    coordinates = []

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
    
    # Coordinates to create a dynamic map boundaries
    try:
        for i in cities.keys():
            if type(cities[i]["coordinates"][0]) == float and type(cities[i]["coordinates"][1]) == float:
                coordinates.append([float(cities[i]["coordinates"][0]), float(cities[i]["coordinates"][1])])
            elif type(cities[i]["coordinates"][0]) == str and type(cities[i]["coordinates"][1]) == str:
                coordinates.append([float(cities[i]["coordinates"][0]), float(cities[i]["coordinates"][1])])
    
        coordinates = numpy.array(coordinates)
        data_frame = pd.DataFrame(coordinates, columns=['Lat', 'Long'])
        sw = data_frame[['Lat', 'Long']].min().values.tolist()
        ne = data_frame[['Lat', 'Long']].max().values.tolist()

        m = Map(close_popup_on_click=False)
        m.fit_bounds([sw, ne])
    except: pass

    # Mapmarker and popup message
    for i in cities.keys():
            try :
                # Create the message of the popup
                message = HTML()
                if cities[i]["message"].count("<hr>") <3 :
                    message.value = cities[i]["message"]
                else : 
                    message.value = str(cities[i]["message"].count("<hr>")) + " letters. There are too many results to show them all here."
                message.description = i.upper()

                # Create the marker
                marker = CircleMarker(location=(cities[i]["coordinates"][0], cities[i]["coordinates"][1]))
                marker.radius = cities[i]["message"].count("<hr>")+3
                marker.fill_opacity = 0.8
                marker.fill_color = "#2A7299"
                marker.stroke = False

                # Add marker on the map
                m.add_layer(marker)
                marker.popup = message
            except: pass

    # If there is no marker created, then the function is recursive and try to take the geolocalisation of
    # contributors instead of coverage place
    if marker == None and first == True :
        show_map(data, "contributor_location", False)
    # If contributor_place and coverage_place were already try, then the function return a dataframe of the data
    elif marker == None and first == False:
        print("An error has been encountered, the map cannot be displayed. We propose to have access to the results in a table format.")
        display(pd.DataFrame(pd.json_normalize(data)))
    else:
        # If the coverage_ülace works, let show the map.
        display(m)


def date_change(change): 
    """
    Handle if a date is selected in a dropdown menu.
    :param change:
    """
    date = change['new']
    if change['type'] == 'change' and change['name'] == 'value':
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
    years = getHumboldtYears(getYears(avoidTupleInList(nested_lookup('date', data))))
    dropdown = createDropdown('', years)
    # If a date is selected in the dropdown menu, then the function
    # date_change is called.
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
    Recursive algorithm which allows 
    a dynamic search with a map visualisation of results.
    :param data: list
    :param search_possibilities: list
    :param flag: bool
    """
    search_by = search_possibilities
    search_dropdown = createDropdown('Search by', search_by)
    
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
        plt = create_histogramm(liste, person)
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


def all_on_map(data, by: str):
    """
    Show all letters of AvH's correspondence
    :param data: List of letters
    :param by: 
    """
    cities = {}
    marker = None
    coordinates = []
    m = Map(
            center=(10, -2),
            zoom=1.5,
            close_popup_on_click=False
            )
    
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
            

    # Mapmarker and popup message
    for i in cities.keys():
            try :
                # Create the message of the popup
                message = HTML()
                if cities[i]["message"].count("<hr>") <3 :
                    message.value = cities[i]["message"]
                else : 
                    message.value = str(cities[i]["message"].count("<hr>")) + " letters. There are too many results to show them all here."
                message.description = i.upper()

                # Create the marker
                marker = CircleMarker(location=(cities[i]["coordinates"][0], cities[i]["coordinates"][1]))
                radius = cities[i]["message"].count("<hr>")+3
                if radius > 10:
                    radius = 12
                marker.radius = radius
                marker.fill_opacity = 0.8
                marker.fill_color = "#2A7299"
                marker.stroke = False

                # Add marker on the map
                m.add_layer(marker)
                marker.popup = message
            except: pass
    display(m)


def sorted_by_period(data:list):
    by_period = {'1830-1859':[], '1829': [], '1806-1828':[], '1805': [], '1799-1804': [], '1792-1798' : []}

    for i in data:
        try :
            date = int(i['date'][:4])
            if date > 1792 and date < 1796:
                by_period['1792-1798'].append(i)
            elif date > 1799 and date < 1804:
                by_period['1799-1804'].append(i)
            elif date == 1805:
                by_period['1805'].append(i)
            elif date > 1806 and date < 1828:
                by_period['1806-1828'].append(i)
            elif date == 1829:
                by_period['1829'].append(i)
            elif date > 1830 and date < 1859:
                by_period['1830-1859'].append(i)
        except: pass

    return by_period


def map_by_period(data, by: str):
    """
    Show all letters of AvH's correspondence with different color for different period of his life.
    There are in total 6 periods represented on the map
    :param data: List of letters
    :param by: what should be on the map represented ? 'coverage_location' or 'contributor_location' ? 
    """
    marker = None
    colors = []
    m = Map(
            center=(10, -2),
            zoom=1.5,
            close_popup_on_click=False
            )

    # Mapmarker and popup message
    for x in data:
        color = "%06x" % random.randint(0, 0xFFFFFF)
        color ='#'+ color
        colors.append(color)
        
        for i in data[x]:
            try :
                # Create the message of the popup
                message = HTML()
                message.value = i["coverage"]

                # Create the marker
                marker = CircleMarker(location=(i['coverage_location']['coordinates'][1],i['coverage_location']['coordinates'][0]))
                marker.radius = 4
                marker.fill_opacity = 0.5
                marker.fill_color = color
                marker.stroke = False

                # Add marker on the map
                m.add_layer(marker)
                marker.popup = message
            except: pass

    display(HTML("<span style='background-color:{};font-weight: bold;'> 1830-1859 </span><span style='background-color:{};font-weight: bold;'> 1829 </span><span style='background-color:{};font-weight: bold;'> 1806-1828 </span><span style='background-color:{};font-weight: bold;'> 1805 </span><span style='background-color:{};font-weight: bold;'> 1799-1804 </span><span style='background-color:{};font-weight: bold;'> 1792-1798 </span>".format(colors[0],colors[1], colors[2], colors[3], colors[4], colors[5])))
    display(m)



