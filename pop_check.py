from multiprocessing import Pool
import requests
import time

downloads_url = 'https://api.npmjs.org/downloads/point/last-month/{}'
dependents_url = 'https://www.npmjs.com/package/{}'
dependents_tag = 'Dependents ('
downloads_scale = 20e5 # Max downloads is express with 17M per month
dependents_scale = 60e2 # Max dependents is lodash with 57K per month

# Monthly downloads
def check_downloads(proj_name):
    r = requests.get(downloads_url.format(proj_name))
    return -1 if r.status_code != requests.codes.ok or 'error' in r.json() else r.json()['downloads']

def check_dependents(proj_name):
    r = requests.get(dependents_url.format(proj_name))
    if r.status_code != requests.codes.ok:
        return -1
    # Scrape the number of dependent projects out
    num_index = r.text.find(dependents_tag)
    if num_index == -1:
        return 0
    i = num_index + len(dependents_tag)
    while i < len(r.text) and r.text[i] != ')':
        i += 1
    return int(r.text[num_index + len(dependents_tag):i])

def popularity_sort(set_names):
    list_names = list(set_names)
    # Query each possible names' popularity
    p = Pool(len(list_names))
    downs = p.map(check_downloads, list_names)
    # Remove packages that do not exist
    for i in reversed(range(len(list_names))):
        if downs[i] == -1:
            del list_names[i]
    deps = p.map(check_dependents, list_names)
    p.close()

    popularity = {}
    for i in range(len(list_names)):
        popularity[list_names[i]] = downs[i] / downloads_scale + deps[i] / dependents_scale
        
    # Sort based on popularity, return only packages which exist
    sorted_names = sorted(list_names, key = lambda x: popularity[x], reverse=True)
    popularity_min_threshold = popularity[sorted_names[0]] / 1e4
    sorted_names_popularities = [(pack, popularity[pack] < popularity_min_threshold) for pack in sorted_names]
    return sorted_names_popularities

if __name__ == "__main__":
    print(popularity_sort(['react','recat', 'rect']))
