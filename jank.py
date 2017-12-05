import sys, subprocess
import pop_check

dryrun_flag = False

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

def insert_char(s, c, i):
    assert len(s) > 0 and len(c) == 1 and i in range(0, len(s) + 1)
    return s[:i] + c + s[i:]

def replace_char(s, c, i, j):
    assert len(s) > 0 and i in range(0, len(s)) and j in range(0, len(s))
    l = list(s)
    if c == None:
        tmp = l[i]
        l[i] = l[j]
        l[j] = tmp
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

def test_typos():
    pack_names = ['react-dom']
    for name in pack_names:
        print(typo_generator(name))

def find_similar_packages(s):
    if s == "leftpda":
        return[s, "leftpad"]
    else:
        return[s]

def run_install(package_name, dryrun=False):
    command = "echo npm install " + package_name
    if dryrun:
        print(command)
    else:
        process = subprocess.Popen(command.split())

if __name__ == "__main__":
    pack_name = sys.argv[1]
    possible_packs = typo_generator(pack_name)
    unfiltered_packs = pop_check.popularity_sort(possible_packs)
    packs = unfiltered_packs
    # packs = filter(unfiltered_packs,
    #                lambda p: p[1] > popularity_min_threshold)

    if len(packs) == 1 and packs[0][0] != pack_name:
        pack_yes = raw_input("Package "
                             + packs[0][0]
                             + " is much more popular than package "
                             + pack_name
                             + "\nDo you want to install "
                             + packs[0][0]
                             + " instead? [y/n] ")
        if pack_yes[0] == "y":
            run_install(packs[0][0], dryrun=dryrun_flag)
        if pack_yes[0] == "n":
            run_install(pack_name, dryrun=dryrun_flag)
    elif len(packs) > 1:
        choices = ""
        for index, (pack, popularity) in enumerate(packs):
            choices += str(index + 1) + ": " + pack + "\n"
        pack_number = raw_input("There are multiple popular packages with similar names.\nWhich package number do you really want?\n"
                                + choices)
        run_install(packs[int(pack_number) - 1][0], dryrun=dryrun_flag)
    else:
        run_install(pack_name, dryrun=dryrun_flag)

