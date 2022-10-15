import pandas as pd
import IPython
from IPython.display import display
import ipywidgets as wgt

from .search_dynamic import show_webpage
from .prepare_data import getJSON, avoidTupleInList, getYears, getHumboldtYears
from .widgets import createDropdown, createButton
from .nestedlookup import *

data = getJSON('data/records.json')


def get_links(links: list):
    """
    Print a list of link for the user.
    :param links: list
    """
    print('Link(s) to online catalogues:')
    for i in links[:15]:
        print('- ' + i)


def onChangeRecipients(change):
    """
    Handle if an addressee has been selected in
    the correspondant dropdown menu
    :param change: 
    :return: dataframe
    """
    # If a addressee is selected in the dropdown menu
    if change['type'] == 'change' and change['name'] == 'value':
        # the selected value is the recipient/addresee
        recipient = change['new']
        results = []
        url = []
        
        # Search of all the letter which were sent to the selected
        # addressee in all data.
        for i in data :
            # Try/Except are used here, because some letters haven't an addressee
                try :
                    if i['subject'] == recipient:
                        results.append(i)
                        # Get the url of the letter in the propre online catalogue
                        # In the kalliope's data, the url is store in the identifier's list
                        # for the other catalog, only the url is stored in the identifier's key.
                        if type(i['identifier']) == list:
                            url.append(i['identifier'][1])
                        else : 
                            url.append(i['identifier'])
                except : 
                    continue
        # If there is only one letter with with the given addressee
        # Then the online catalogue's page of the letter will be in the
        # jupyter notebook shown. 
        if len(results) == 1 :
            if type(results[0]['identifier']) == list:
                show_webpage(results[0]['identifier'][1])
            else : 
                show_webpage(results[0]['identifier'])
        # Else: results are shown in a dataframe (table) and the 
        # url links to the online catalogues are listed.
        else : 
            display(pd.DataFrame(pd.json_normalize(results)))
            get_links(url)        

def onChangeCreators(change): 
    """
    Handle if a sender has been selected in
    the correspondant dropdown menu
    :param change: 
    :return: dataframe
    """
    # If a sender is selected in the dropdown menu
    if change['type'] == 'change' and change['name'] == 'value':
        # the selected value is the sender which called creator in the API's metadata
        sender = change['new']
        results = []
        url = []
        
        # Search of all the letter sent by the selected sender.
        for i in data :
                try :
                    if i['creator'] == sender:
                        results.append((i))
                        # Get the url of the letter in the propre online catalogue
                        # In the kalliope's data, the url is store in the identifier's list
                        # for the other catalog, only the url is stored in the identifier's key.
                        if type(i['identifier']) == list:
                            url.append(i['identifier'][1])
                        else : 
                            url.append(i['identifier'])
                except : 
                    continue
        # If there is only one letter with with the given addressee
        # Then the online catalogue's page of the letter will be in the
        # jupyter notebook shown. 
        if len(results) == 1 :
            if type(results[0]['identifier']) == list:
                show_webpage(results[0]['identifier'][1])
            else : 
                show_webpage(results[0]['identifier'])

        # Else : results are shown in a dataframe (table) and the 
        # url links to the online catalogues are listed.
        else : 
            display(pd.DataFrame(pd.json_normalize(results)))
            get_links(url)

def onChangePlaces(change):
    """
    Handle if a place has been selected in
    the correspondant dropdown menu
    :param change: 
    :return: dataframe
    """
    # If a place is selected in the dropdown menu
    if change['type'] == 'change' and change['name'] == 'value':
        # the selected value is the coverage place which called coverage in the API's metadata
        place = change['new']
        results = []
        url = []
        
        # Search of all the letter with the selected value as coverage place.
        for i in data :
                try :
                    if i['coverage'] == place:
                        results.append(i)
                        # Get the url of the letter in the propre online catalogue
                        # In the kalliope's data, the url is store in the identifier's list
                        # for the other catalog, only the url is stored in the identifier's key.
                        if type(i['identifier']) == list:
                            url.append(i['identifier'][1])
                        else : 
                            url.append(i['identifier'])
                except : 
                    continue
        # If there is only one letter with with the given addressee
        # Then the online catalogue's page of the letter will be in the
        # jupyter notebook shown.
        if len(results) == 1 :
            if type(results[0]['identifier']) == list:
                show_webpage(results[0]['identifier'][1])
            else : 
                show_webpage(results[0]['identifier'])
        # Else : results are shown in a dataframe (table) and the 
        # url links to the online catalogues are listed.
        else : 
            display(pd.DataFrame(pd.json_normalize(results)))
            get_links(url)



def onChangeDate(change): 
    """
    Handle if a date has been selected in
    the correspondant dropdown menu
    :param change: 
    :return: dataframe
    """
    # If a date is selected in the dropdown menu
    if change['type'] == 'change' and change['name'] == 'value':
        # the selected value is the year of the date of sending
        date = change['new']
        results = []
        url = []

        # Search of all the letter with the selected value as year of the date of sending
        for i in data :
                try :
                    if date in i['date']:
                        results.append(i)
                        # Get the url of the letter in the propre online catalogue
                        # In the kalliope's data, the url is store in the identifier's list
                        # for the other catalog, only the url is stored in the identifier's key.
                        if type(i['identifier']) == list:
                            url.append(i['identifier'][1])
                        else : 
                            url.append(i['identifier'])
                except : 
                    continue
        # If there is only one letter with with the given addressee
        # Then the online catalogue's page of the letter will be in the
        # jupyter notebook shown.
        if len(results) == 1 :
            if type(results[0]['identifier']) == list:
                show_webpage(results[0]['identifier'][1])
            else : 
                show_webpage(results[0]['identifier'])
        # Else : results are shown in a dataframe (table) and the 
        # url links to the online catalogues are listed.
        else : 
            display(pd.DataFrame(pd.json_normalize(results)))
            get_links(url)


def onChangeInstitution(change): 
    """
    Handle if an institution has been selected in
    the correspondant dropdown menu
    :param change: 
    :return: dataframe
    """
    fb = getJSON("data/edh_findbuch.json")
    if change['type'] == 'change' and change['name'] == 'value':
        institution = change['new']
        results = []
        url = []
        for i in fb:
            if institution == i['institution']:
                print("In the analogue collection of the BBAW (K. Nr." + i['k_nr'] + "): ")
                if i['vonH']:
                    print(i['vonH'] + " letters by AvH")
                if i['anH']: 
                    print(i['anH'] + " letters to AvH")
                if i['sonst']: 
                    print(i['sonst'] + " others documents")
                try:
                    print(str(int(i['vonH'])+int(i['anH'])+int(i['sonst'])) + " Total of documents.")
                except: pass
        
        for i in data:
                try :
                    if i['contributor'] == institution:
                        results.append(i)
                        if type(i['identifier']) == list:
                            url.append(i['identifier'][1])
                        else : 
                            url.append(i['identifier'])
                except : 
                    continue
        if len(results) == 1 :
            if type(results[0]['identifier']) == list:
                show_webpage(results[0]['identifier'][1])
            else : 
                show_webpage(results[0]['identifier'])
        else : 
            print("Today in the online catalogues : " + str(len(results)) + " results")
            
            content = {"document": 0, "letter": 0, "other": 0}
            for r in results: 
                try :
                    format = r["format.extent"].lower()
                    if "lett" in format:
                        nb_letter = format.split(" lett")[0]
                        if "extrait" in nb_letter:
                            nb_letter = nb_letter.split(" extr")[0]
                        try:
                            content["letter"] += int(nb_letter)
                        except: print(format)
                    elif "brief" in r["format.extent"].lower():
                        nb_letter = r["format.extent"].lower().split(" brief")[0]
                        try:
                            content["letter"] += int(nb_letter)
                        except : pass
                    elif "do" in r["format.extent"].lower():
                        nb_doc = r["format.extent"].lower().split(" do")[0]
                        content["document"] += int(nb_doc)
                    else :
                        nb_other = r["format.extent"].lower().split(" ")[0]
                        try:
                            content["other"] += int(nb_other)
                        except: content["other"] += 1
                except: pass
            print(content)
            display(pd.DataFrame(pd.json_normalize(results)))
            if results:
                get_links(url)


def search_institutions(data:dict):
    """
    Create a dropdown menu with all stockholding institutions
    :param data: dict 
    :return: dropdown menu
    :rtype: widget
    """
    fb = getJSON("data/edh_findbuch.json")
    institutions = nested_lookup('contributor', data)
    for i in fb:
        if i['institution'] not in institutions:
                    institutions.append(i['institution'])
    dropdown = createDropdown('', institutions)
    dropdown.observe(onChangeInstitution)
    return dropdown


def search_creators(data:dict):
    """
    Create a dropdown menu with all senders
    :param data: dict 
    :return: dropdown menu
    :rtype: widget
    """
    creators = avoidTupleInList(nested_lookup('creator', data))
    dropdown = createDropdown('', creators)
    dropdown.observe(onChangeCreators)
    return dropdown

def search_recipient(data:dict):
    """
    Create a dropdown menu with all addressee
    :param data: dict 
    :return: dropdown menu
    :rtype: widget
    """
    recipients = avoidTupleInList(nested_lookup('subject', data))
    recipients.remove('Humboldt, Alexander von (1769-1859)')
    dropdown = createDropdown('', recipients)
    dropdown.observe(onChangeRecipients)
    return dropdown    


def search_cvg_places(data:dict):
    """
    Create a dropdown menu with all coverage places
    :param data: dict 
    :return: dropdown menu
    :rtype: widget
    """
    places = avoidTupleInList(nested_lookup('coverage', data))
    dropdown = createDropdown('', places)
    dropdown.observe(onChangePlaces)
    return dropdown

def search_date(data:dict):
    """
    Create a dropdown menu with all years when a letter 
    (to and by AvH) has been sent
    :param data: dict 
    :return: dropdown menu
    :rtype: widget
    """
    years = getHumboldtYears(getYears(avoidTupleInList(nested_lookup('date', data))))
    dropdown = createDropdown('', years)
    dropdown.observe(onChangeDate)
    return dropdown 
