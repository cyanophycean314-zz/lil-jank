from multiprocessing import Pool
import requests
import time

downloads_url = 'https://api.npmjs.org/downloads/point/last-month/{}'
dependents_url = 'https://www.npmjs.com/package/{}'
dependents_tag = 'Dependents ('
downloads_scale = 20e5 # Max downloads is express with 17M per month
dependents_scale = 60e2 # Max dependents is lodash with 57K per month
popularity_min_threshold = 1e-3 # Min popularity for package to be considered

# Monthly downloads
def check_downloads(proj_name):
    r = requests.get(downloads_url.format(proj_name))
    if r.status_code != requests.codes.ok or 'error' in r.json():
        return -1
    return r.json()['downloads']

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

# -1 means project does not exist. Otherwise popularity is nonnegative and higher is better
def get_popularity(proj_name):
    downloads = check_downloads(proj_name)
    if downloads == -1:
        return -1
    dependents = check_dependents(proj_name)
    # print('{}: {}, {}'.format(proj_name, downloads, dependents))
    return (downloads / downloads_scale) + (dependents / dependents_scale)

def popularity_sort(set_names):
    list_names = list(set_names)
    # Query each possible names' popularity
    start_time = time.time()
    p = Pool(len(list_names))
    downs = p.map(check_downloads, list_names)
    deps = p.map(check_dependents, list_names)
    end_time = time.time()
    print('Network time: {}'.format(end_time - start_time))

    popularity = {}
    for i in range(len(list_names)):
        popularity[list_names[i]] = -1 if downs[i] == -1 else downs[i] / downloads_scale + deps[i] / dependents_scale
        
    # Sort based on popularity, return only packages which exist
    sorted_names = sorted(list_names, key = lambda x: popularity[x], reverse=True)
    while sorted_names and popularity[sorted_names[-1]] < popularity_min_threshold:
        sorted_names.pop()
    sorted_names_popularities = [(pack, popularity[pack]) for pack in sorted_names]
    return sorted_names_popularities

if __name__ == "__main__":
    print(popularity_sort(['react','recat', 'rect']))
