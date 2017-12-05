
import requests

downloads_url = 'https://api.npmjs.org/downloads/point/last-month/{}'
dependents_url = 'https://www.npmjs.com/package/{}'
dependents_tag = 'Dependents ('
downloads_scale = 20e5 #Max downloads is express with 17M per month
dependents_scale = 60e2 #Max dependents is lodash with 57K per month

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
    #Scrape the number of dependent projects out
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

def popularity_sort(list_names):
    #Query each possible names' popularity
    popularity = {}
    for proj in list_names:
        popularity[proj] = get_popularity(proj)
    # print(popularity)
    # Sort based on popularity, return only packages which exist
    sorted_names = sorted(list_names, key = lambda x: popularity[x], reverse=True)
    while popularity[sorted_names[-1]] == -1:
        sorted_names.pop()
    return sorted_names

if __name__ == "__main__":
    print(popularity_sort(['react','recat']))
