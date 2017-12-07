import datetime, requests, os, sys, subprocess, time
import pop_check, script_check, typo
from dateutil import parser

dryrun_flag = False
time_flag = True

node_core_modules = ["http","events","util","domain","cluster", \
"buffer","stream","crypto","tls","fs","string_decoder","path","net",\
"dgram","dns","https","url","punycode","readline","repl","vm",\
"child_process","assert","zlib","tty","os","querystring"]

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

def run_install(package_name, dryrun=False):
    command = "echo npm install " + package_name
    if dryrun:
        print(command)
    else:
        process = subprocess.Popen(command.split())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python3 jank.py <package>')
        sys.exit(1)

    print('Verifying package security')

    if time_flag:
        start = time.time()

    pack_name = sys.argv[1]
    possible_packs = typo.typo_generator(pack_name)

    if time_flag:
        end = time.time()
        print("Typo generation took " + str(end - start) + " seconds")

    if time_flag:
        start1 = time.time()

    unfiltered_packs = pop_check.popularity_sort(possible_packs)
    packs = unfiltered_packs

    if time_flag:
        end1 = time.time()
        print("Popularity check took " + str(end1 - start1) + " seconds")

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
        if script_check.check_scripts(chosen_name):
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

