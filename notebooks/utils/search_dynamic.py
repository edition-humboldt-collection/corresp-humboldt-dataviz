import pandas as pd
import IPython
from IPython.display import display, HTML, IFrame, Javascript
import ipywidgets as wgt

from .prepare_data import getJSON, avoidTupleInList, getYears 
from .widgets import createDropdown, createButton
from .nestedlookup import *


data = getJSON('data/records.json')


def show_webpage(link:str):
    """
    Return the web page of the param link
    :param link: str 
    :return: IFrame
    """
    return display(IPython.display.IFrame(link, 1550, 750)) 


def btn_new_search():
    """
    Create a new search button.
    :return: btn
    :rtype: button
    """
    # Create the button
    btn = createButton('New search', 'info')
    output = wgt.Output()

    def new_search(b):
        # This function clears the ouput of a jupyter cell
        with output : 
            display(Javascript('IPython.notebook.execute_cell()'))
    
    # When the button is clicked, then the output of the jupyter
    # cell will be clean.
    btn.on_click(new_search)
    return btn


def search(data, search_possibilities, flag : bool):
    """
    Recursive function for a dynamic search in the data.
    :param data: dict
    :param search_possibilities: list
    :param flag: bool 
    :return: Dropdown menu for further research into the data or the result of the search
    """
    search_by = search_possibilities
    search_dropdown = createDropdown('Search by', search_by)
    
    def show_results(results):
        """
        Handle to show or not results of the dynamic search.
        :param results: dict
        :return: show_webpage() or DataFrame or search()
        :rtype: functions or DataFrame
        """
        # If there is no more possibilities to search in the data 
        # or there is one letter as result
        if len(search_by) <=1 or len(results) <2:
                # If there is one letter left as result
                if len(results) == 1 :
                    try :
                        # then the webpage of the online catalogue
                        # when the letter is stored is shown.
                        if type(results[0]['identifier']) == list:
                            # Get the url of the letter in the proper online catalogue
                            # In the kalliope's data, the url is store in the identifier's list
                            # for the other catalog, only the url is stored in the identifier's key.
                            show_webpage(results[0]['identifier'][1])
                        else : 
                            show_webpage(results[0]['identifier'])
                    except:
                        # If there isn`t an url for this letter, then the list of the institution 
                        # from the analogue collection of the BBAW is shown in detail.
                        for i in results:
                            print("In the analogue collection of the BBAW (K. Nr." + i['k_nr'] + "): ")
                            if i['vonH']:
                                print(i['vonH'] + " letters by AvH")
                            if i['anH']: 
                                print(i['anH'] + " letters to AvH")
                            if i['sonst']: 
                                print(i['sonst'] + " others documents")
                                try : 
                                    print(str(int(i['vonH'])+int(i['anH'])+int(i['sonst'])) + " is the total of documents.")
                                except: pass
                else : 
                    display(pd.DataFrame(pd.json_normalize(results)))
        # If there is more than one letter left as result and there are still
        # searching possibilities, then the function itself is call
        else : 
            search(results, search_by, False)

    def change_creators(change):
        """
        Handle if a sender has been selected in
        the correspondant dropdown menu
        :param change: 
        :return: show_results
        """
        # If a creator/sender is selected in the dropdown menu
        if change['type'] == 'change' and change['name'] == 'value':
            # the selected value is sender
            sender = change['new']
            results = []
            # Search of all letters with the selected value as sender
            # in the metadata the sender value is stored on the `creator` key
            for r in data:
                try :
                    if r['creator'] == sender:
                        # Correspondant letters are stored in the `results` list
                        results.append(r)
                except : 
                    continue
            
            # Search by sender is removed of the searching possibilities
            search_by.remove('Sender letters (to AvH)')
            # Addressee is also removed of the searching possibilities list
            # Because if the user searched by sender the addressee could be only Humboldt
            search_by.remove('Addressee letters (by AvH)')
            # Results are handled by the show_results function
            show_results(results)

    def change_recipients(change):
        """
        Handle if an addressee has been selected in
        the correspondant dropdown menu
        :param change: 
        :return: show_results
        """
        # If a creator/sender is selected in the dropdown menu
        if change['type'] == 'change' and change['name'] == 'value':
            # the selected value is the addressee
            addressee = change['new']
            results = []
            # Search of all letters with the selected value as addressee
            # in the metadata the addressee value is stored on the `subject` key
            for r in data:
                try :
                    if r['subject'] == addressee:
                        # Correspondant letters are stored in the `results` list
                        results.append(r)
                except : 
                    continue
            # Search by addressee is removed of the searching possibilities
            search_by.remove('Addressee letters (by AvH)')
            # Sender is also removed of the searching possibilities list
            # Because if the user searched by addressee the sender could be only Humboldt
            search_by.remove('Sender letters (to AvH)')
            # Results are handled by the show_results function
            show_results(results)

    def change_date(change):
        """
        Handle if a date has been selected in
        the correspondant dropdown menu
        :param change: 
        :return: show_results
        """
        # If a data is selected in the dropdown menu
        if change['type'] == 'change' and change['name'] == 'value':
            # the selected value is the data
            date = change['new']
            results = []
            # Search of all letters with the selected value as date
            for r in data:
                try :
                    if date in r['date']:
                        # Correspondant letters are stored in the `results` list
                        results.append(r)
                except : 
                    continue
            # Search by date is removed of the searching possibilities
            search_by.remove('Date')
            # Results are handled by the show_results function
            show_results(results)
            
            
    def change_institution(change): 
        """
        Handle if an institution has been selected in
        the correspondant dropdown menu
        :param change: 
        :return: show_results
        """
        # This function searchs in institutions who put their data on kalliope
        # but also institutions which are in the analog collection of the BBAW. We know
        # the number of documents related to Humbolt stored by theses institutions
        #  but contents of these documents aren´t digitalized and stored in an digital database. 
        fb = getJSON("data/edh_findbuch.json")
        data_institutions = nested_lookup('contributor', data)

        # If an institution is selected in the dropdown menu
        if change['type'] == 'change' and change['name'] == 'value':
            # the selected value is the institution
            institution = change['new']
            results = []
            # If the insitution not our data
            if institution not in data_institutions:
                # then it searchs in the institutions of the BBAW´s analog collection 
                for i in fb:
                    if institution == i['institution']:
                        # Correspondant results are stored in the `results` list
                        results.append(i)
            # Else : the institution is in our data
            else :    
                # Search of all letters with selected value as institution
                # In the metadata, the insitution is stored unter the `contributor` key
                for r in data :
                    try :
                        if r['contributor'] == institution:
                            # Correspondant letters are stored in the `results` list
                            results.append(r)
                    except : 
                        continue
            # Search by institions is removed of the searching possibilities
            search_by.remove('Stockholding institution')  
            # Results are handled by the show_results function
            show_results(results)


    def change_place(change): 
        """
        Handle if a place has been selected in
        the correspondant dropdown menu
        :param change: 
        :return: show_results
        """
        # If a place is selected in the dropdown menu
        if change['type'] == 'change' and change['name'] == 'value':
            # the selected value is the place
            place = change['new']
            results = []
            # Search of all letters with the selected value as coverage place
            # In the metadata, the coverage place is stored under the `coverage` key
            for r in data :
                try :
                    if r['coverage'] == place:
                        # Correspondants letters are stored in the `results` list
                        results.append(r)
                except : 
                    continue
            # Search by places is removed of the searching possibilities
            search_by.remove('Coverage place')
            # Results are handled by the show_results function
            show_results(results)


    def no_element_for_dropdown(data :dict, searching_by, element: str):
        """
        :param data: dict
        :param searching_by: list
        :param element: str
        :return: search()
        """
        search_by.remove(element)
        print('There is {0} registered for these data.'.format(element.lower()))
        search(data, search_by, False)

    
    def change_search(change): 
        """
        Manage what the user wants to search by
        :param change: 
        """
        # If a value is selected in the dropdown menu
        if change['type'] == 'change' and change['name'] == 'value':
            # Search by sender
            if change['new'] == 'Sender letters (to AvH)' and change['type'] == 'change':
                # In the data, the sender are called `creator`
                # Create a list of all creators from data
                creators = avoidTupleInList(nested_lookup('creator', data))
                # If there are no creator
                if len(creators) == 0:
                    # it´s impossible to create a dropdown menu
                    return no_element_for_dropdown(data, search_by, change['new'] )
                
                # If there are creators
                else :
                    # Creation of the dropdown menu with all creator´s name
                    dropdown = createDropdown('Senders', creators)
                    dropdown.observe(change_creators) 
            # Search by addressee
            elif change['new'] == 'Addressee letters (by AvH)' and change['type'] == 'change':
                recipients = avoidTupleInList(nested_lookup('subject', data))
                if len(recipients) == 0:
                    return no_element_for_dropdown(data, search_by, change['new'] )
                else :
                    dropdown = createDropdown('Recipients', recipients)
                    dropdown.observe(change_recipients)
            # Search by date
            elif change['new'] == 'Date' and change['type'] == 'change':
                years = getYears(avoidTupleInList(nested_lookup('date', data)))
                if len(years) == 0:
                    return no_element_for_dropdown(data, search_by, change['new'] )
                else :
                    dropdown = createDropdown('Dates', years)
                    dropdown.observe(change_date)
            # Search by institution
            elif change['new'] == 'Stockholding institution' and change['type'] == 'change':
                # Search is in the data but also in the BBAW´s analog collection
                fb = getJSON("data/edh_findbuch.json")
                institutions = nested_lookup('contributor', data)
                if len(institutions) == 4693 :
                    for i in fb:
                        if i['institution'] not in institutions:
                            institutions.append(i['institution'])
                if len(institutions) == 0:
                    return no_element_for_dropdown(data, search_by, change['new'] )
                else :
                    dropdown = createDropdown('Institutions', institutions)
                    dropdown.observe(change_institution)
            # Search by place
            elif change['new'] == 'Coverage place' and change['type'] == 'change':
                places = avoidTupleInList(nested_lookup('coverage', data))
                if len(places) == 0:
                    return no_element_for_dropdown(data, search_by, change['new'] )
                else :
                    dropdown = createDropdown('Places', places)
                    dropdown.observe(change_place)
            display(dropdown)
    
    search_dropdown.observe(change_search)

    # If it is a first or a new search
    if flag == True:
        # Only one dropdown menu will be shown
        return search_dropdown
    else :
        # else an additional dropdown menu will be display
        return display(search_dropdown)
