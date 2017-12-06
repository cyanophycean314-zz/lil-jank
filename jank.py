import datetime, requests, os, sys, subprocess, tarfile, json, time
import pop_check
from dateutil import parser
import urllib.request 
from pprint import pprint

dryrun_flag = False
time_flag = False

close_letters = {
    'q': {'w', 'a'},
    'a': {'z', 's', 'q'},
    'z': {'a', 'x'},
    'w': {'q', 'e'},
    's': {'a', 'd'},
    'x': {'z', 'c'},
    'e': {'w', 'r'},
    'd': {'s', 'f'},
    'c': {'x', 'v'},
    'r': {'e', 't'},
    'f': {'d', 'g'},
    'v': {'c', 'b'},
    't': {'r', 'y'},
    'g': {'f', 'h'},
    'b': {'v', 'n'},
    'y': {'t', 'u'},
    'h': {'g', 'j'},
    'n': {'b', 'm'},
    'u': {'y', 'i'},
    'j': {'h', 'k'},
    'm': {'b', 'm'},
    'i': {'u', 'o'},
    'k': {'j', 'l'},
    'o': {'i', 'p', 'l'},
    'l': {'k', 'o'},
    'p': {'o'}
}

node_core_modules = ["http","events","util","domain","cluster", \
"buffer","stream","crypto","tls","fs","string_decoder","path","net",\
"dgram","dns","https","url","punycode","readline","repl","vm",\
"child_process","assert","zlib","tty","os","querystring"]

unsafe_keywords = ["http", "request", "process.env", "rm", \
"password", "username", "host", "network"]

repository_url = 'https://registry.npmjs.org/{}'

def check_warnings(proj_name):
    has_warning = False
    # check if name of core module
    if proj_name in node_core_modules:
        has_warning = True
        print('This module is a core node module. You probably do not need to install this.')

    # check if package less than one day old
    r = requests.get(repository_url.format(proj_name))
    if r.status_code == requests.codes.ok and 'error' not in r.json():
        creation_date = parser.parse(r.json()['time']['created'])
        diff =  datetime.datetime.now(datetime.timezone.utc) - creation_date
        if diff.days < 1:
            has_warning = True
            print('This module is less than a day old and has not been vetted yet. Installing this package is not advised')

    if has_warning:
        return input('Please retype the package name you wish to install: ').strip() != proj_name
    return False

def insert_char(s, c, i):
    assert len(s) > 0 and len(c) == 1 and i in range(0, len(s) + 1)
    return s[:i] + c + s[i:]

def replace_char(s, c, i, j):
    assert len(s) > 0 and i in range(0, len(s)) and j in range(0, len(s))
    l = list(s)
    if c == None:
        l[i], l[j] = l[j], l[i]
    else:
        l[i] = c
    return ''.join(l)

def delete_char(s, i):
    assert len(s) > 0 and i in range(0, len(s))
    return s[:i] + s[i+1:]

def typo_generator(s):
    results = set()
    results.add(s.replace('-',''))

    for i, char in enumerate(s):
        fat_finger = close_letters.get(char)
        if fat_finger != None:
            for letter in fat_finger:
                results.add(insert_char(s, letter, i))
                results.add(insert_char(s, letter, i+1))
                results.add(replace_char(s, letter, i, i))

        results.add(delete_char(s, i))
        results.add(insert_char(s, '-', i))

        for j, _ in enumerate(s):
            results.add(insert_char(s, char, j))
            results.add(replace_char(s, None, i, j))
    return results

def find_similar_packages(s):
    if s == "leftpda":
        return[s, "leftpad"]
    else:
        return[s]

def test_typos():
    pack_names = ['react-dom']
    for name in pack_names:
        print(typo_generator(name))

def run_install(package_name, dryrun=False):
    command = "echo npm install " + package_name
    if dryrun:
        print(command)
    else:
        process = subprocess.Popen(command.split())

def extract(tar_url, extract_path='.'):
    tar = tarfile.open(tar_url, 'r')
    for item in tar:
        tar.extract(item, extract_path)
        if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
            extract(item.name, "./" + item.name[:item.name.rfind('/')])

def check_script(script):
    strings = script.split(" ")
    if strings[0] == "node":
        file = open("package/" + strings[1], "r")
        for line in file:
            for keyword in unsafe_keywords:
                if keyword in line:
                    return True
    else:
        for string in strings:
            for keyword in unsafe_keywords:
                if keyword in string:
                    return True
    return False

def check_scripts(package_name):
    command = "npm view " + package_name + " dist.tarball"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    url = output[:len(output)-1].decode("utf-8")
    filename = package_name + ".tgz"
    urllib.request.urlretrieve(url, filename)
    extract(filename)
    pkg_json = json.load(open('package/package.json'))
    if pkg_json.get("scripts") != None:
        #pprint(pkg_json.get("scripts"))
        check_script(pkg_json.get("scripts").get("preinstall"))
        check_script(pkg_json.get("scripts").get("postinstall"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python3 jank.py <package>')
        sys.exit(1)

    print('Verifying package security')

    if time_flag:
        start = time.time()
    check_scripts('janksum')

    pack_name = sys.argv[1]
    possible_packs = typo_generator(pack_name)
    unfiltered_packs = pop_check.popularity_sort(possible_packs)
    packs = unfiltered_packs

    if time_flag:
        end = time.time()
        print("Typo generation and popularity check took " + str(end - start) + " seconds")

    chosen_name = pack_name
    # 1 more popular package
    if len(packs) == 1 and packs[0][0] != pack_name:
        pack_yes = input(("Package {} is much more popular than package {}\n"
                          + "Do you want to install {} instead? [y/n]? ")
                         .format(packs[0][0], pack_name, packs[0][0]))
        if pack_yes[0] == "y":
            chosen_name = packs[0][0]
        elif pack_yes[0] == "n":
            chosen_name = pack_name
        else:
            while pack_yes[0] not in 'yn':
                pack_yes = input("Please enter [y/n] ")
    # More than 1 popular package
    elif len(packs) > 1:
        choices = ""
        packs.append((pack_name, 0))
        for index, (pack, _popularity) in enumerate(packs):
            choices += str(index + 1) + ": " + pack + (' (unpopular)' if pack == pack_name else '') + "\n"
        pack_number = ''
        while not pack_number.isdigit() or int(pack_number) <= 0 or int(pack_number) > len(packs):
            pack_number = input("There are multiple popular packages with similar names.\n"
                                + "Which package number do you really want?\n"
                                + choices)
            
        chosen_name = packs[int(pack_number) - 1][0]

    # Perform final checks on core modules, scripts, and youthfulness
    if not check_warnings(chosen_name):
        if time_flag:
            start2 = time.time()
        if not check_scripts(chosen_name):
            install_yes = input("Warning: dangerous behavior has been detected in the preinstall or postinstall scripts.\n"
                    + "Are you sure you want to install? [y/n]\n")
            if install_yes[0] == "y":
                run_install(chosen_name, dryrun=dryrun_flag)
                exit()
            elif install_yes[0] == "n":
                exit()
            else:
                while install_yes[0] not in 'yn':
                    install_yes = input("Please enter [y/n] ")
        if time_flag:
            end2 = time.time()
            print("Script check took " + str(end2 - start2) + " seconds")
        run_install(chosen_name, dryrun=dryrun_flag)

