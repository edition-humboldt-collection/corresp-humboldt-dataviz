from ipyleaflet import Map, Marker, Popup
from ipywidgets import HTML
from nested_lookup import nested_lookup
import matplotlib.pyplot as plt
import gender_guesser.detector

from widgets import createDropdown, createButton, createCheckBox
from prepare_data import getJSON, avoidTupleInList


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


def show_contributors(data: list, by : str, first: bool):
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
                    cities[city] = {'message' : '', 'coordinates':[]}
                    if 'Humboldt' in i['creator']:
                        who = i['creator']
                    cities[city]["message"] = i['title'] + "<br><i>"+ i["contributor"] +"</i> <br> <a href=\""+ i["identifier"][1] + "\" target=\"_blank\">auf Kalliope</a> <hr>"
                    cities[city]["coordinates"] = [i[by]["coordinates"][1], i[by]["coordinates"][0]]
                elif i[by]["address"] in cities:
                    city = i[by]["address"]
                    cities[city]["message"] = cities[city]["message"] + " </b> " + i["title"] + "<br><i>"+ i["contributor"]  + "</i><br> <a href=\""+ i["identifier"][1] + "\" target=\"_blank\">auf Kalliope</a> <hr>"
            except : pass

    
    for i in cities.keys():
            try :
                message = HTML()
                if cities[i]["message"].count("<hr>") <3 :
                    message.value = cities[i]["message"]
                else : 
                    message.value = cities[i]["message"].split('<hr>')[0] + '<hr>' + str(cities[i]["message"].count("<hr>")-1) + " andere Briefe. Es ist aber zu viele Ergebnisse, um alle hier zu zeigen."
                message.description = i.upper()
                marker = Marker(location=(cities[i]["coordinates"][0], cities[i]["coordinates"][1]))
                m.add_layer(marker)
                marker.popup = message
            except: pass

    display(m)
    
       
    
def women_change(change): 
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
        show_contributors(results, 'contributor_location', True)
            
        # create the histogramm
        title = 'Anzahl des Briefwechsels zwischen AvH(1769-1859) und ' + person
        x_coords = [coord[0] for coord in liste]
        y_coords = [coord[1] for coord in liste]
        fig= plt.figure(figsize=(10,5))
        plt.hist(x_coords, bins=30)
        fig.suptitle(title, fontsize=12)
        plt.xlabel('Jahr', fontsize=12)
        plt.ylabel('Anzahl der Briefe', fontsize=12)
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
