import json


def writeJSON(file, data):
    """
    Store JSON data in a JSON file 
    :param file: str
    :param data: dict
    """
    with open(file, mode='w') as f:
        json.dump(data, f)


def getJSON(path):
    """
    Get data from a JSON file 
    :param path: str
    :return: data
    :rtype: dict
    """
    with open(path, encoding="iso-8859-15" ) as data_file:
       data = json.load(data_file)
    return data;


def avoidTupleInList(data : list):
    """
    Remove the tuple of a list 
    :param data: list
    :return: clean_data
    :rtype: list
    """
    clean_data = []
    for i in data :
        if type(i) != list:
            clean_data.append(i)
    return clean_data


def getYears(dates :list):
    """
    Give all the years of a list of dates
    :param dates: list
    :return: results
    :rtype: list
    """
    results = []
    for i in dates:
        results.append(i[:4])
    return results


def getHumboldtYears(dates:list):
    """
    Give only years of Humboldt's life
    :param dates: list
    :return: results
    :rtype: list
    """
    results = []
    for i in dates:
        try:
            if int(i) > 1769  and int(i) < 1859 :
                results.append(i)
        except: pass
    return results