from ipyleaflet import Map, Marker, Popup
from ipywidgets import HTML
from nested_lookup import nested_lookup
import matplotlib.pyplot as plt
import gender_guesser.detector

from .widgets import createDropdown, createButton, createCheckBox
from .prepare_data import getJSON, avoidTupleInList
from .mapviz import show_map, create_histogramm


data = getJSON('data/records.json')

def women_partner():
    guess = gender_guesser.detector.Detector()
    data_women = []

    # Letters to AvH
    for i in data:
        try :
            if 'Humboldt' not in i['creator'] and 'Unbekannt' not in i['creator'] and type(i['creator']) != list:
                firstname = i['creator'].split(' ')[0]
                gender =guess.get_gender(firstname)
                if gender == 'unknown':
                    firstname = i['creator'].split(', ')[1].split(' (')[0]
                    gender =guess.get_gender(firstname)
                
                    if ' ' in firstname :
                        firstname = firstname.split(' ')[0]
                    elif '-' in firstname :
                        firstname = firstname.split('-')[0]

                if firstname == 'Henriette':
                    gender = 'female'
                else : 
                    gender = guess.get_gender(firstname)
                    
            if 'female' in gender:
                data_women.append(i)
        except: pass

    # Letters by AvH
    for i in data:
        try :
            if 'Humboldt' not in i['subject'] and 'Unbekannt' not in i['subject'] and type(i['subject']) != list:
                firstname = i['subject'].split(' ')[0]
                gender = guess.get_gender(firstname)
                if gender == 'unknown':
                    firstname = i['subject'].split(', ')[1].split(' (')[0]
                    gender =guess.get_gender(firstname)
                    if ' ' in firstname :
                        firstname = firstname.split(' ')[0]
                    elif '-' in firstname :
                        firstname = firstname.split('-')[0]

                    if firstname == 'Henriette':
                        gender = 'female'
                    else : 
                        gender =guess.get_gender(firstname)
                    
            if 'female' in gender:
                data_women.append(i)
        except: pass

    return data_women
       
    
def women_change(change): 
    """
    Handle if a woman's name has been selected in
    the correspondant dropdown menu
    :param change: 
    :return: show_results
    """
    if change['type'] == 'change' and change['name'] == 'value':
        person = change['new']
        results = []
        # get the corresponding letters
        for i in data:
            try : 
                if change['new'] in i["creator"] or change['new'] in i["subject"]:
                    results.append(i)
            except: pass
        
        # from corresponding letters, get and transform the data to build the histogramm
        liste = []
        for i in results:
            try :
                if int(i['date'][:4]) <1859:
                    liste.append((int(i['date'][:4]), int(1)))
            except: 
                pass
        show_map(results, 'contributor_location', True)
            
        # create the histogramm
        plt = create_histogramm(liste, person)
        plt.show()


def by_women(data:dict):
    """
    Function that creates a dropdown menu of all persons 
    who have received and/or sent at least one letter 
    for which a date is recorded
    :param data: dict
    :return: dropdown menu
    :rtype: widget
    """
 
    # Get all people who received or sent a letter    
    creators = avoidTupleInList(nested_lookup('creator', data))
    subjects = avoidTupleInList(nested_lookup('subject', data))
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
    dropdown.observe(women_change)
    return dropdown 
