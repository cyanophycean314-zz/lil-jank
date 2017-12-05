import sys

def insert_char(s, c, i):
    assert len(s) > 0 and len(c) == 1 and i in range(0, len(s) + 1)
    return s[:i] + c + s[i:]

def replace_char(s, i, j):
    assert len(s) > 0 and i in range(0, len(s)) and j in range(0, len(s))
    l = list(s)
    tmp = l[i]
    l[i] = l[j]
    l[j] = tmp
    return ''.join(l)

def delete_char(s, i):
    assert len(s) > 0 and i in range(0, len(s))
    return s[:i] + s[i+1:]

def typo_generator(s):
    results = set()

    for i, char in enumerate(s):
        results.add(delete_char(s, i))
        results.add(insert_char(s, '-', i))
        for j, _ in enumerate(s):
            results.add(insert_char(s, char, j))
            results.add(replace_char(s, i, j))
    return results

def test_typos():
    pack_names = ['reactdom']
    for name in pack_names:
        print(typo_generator(name))

def find_similar_packages(s):
    if s == "leftpda":
        return[s, "leftpad"]
    else:
        return[s]

if __name__ == "__main__":
    """
    pack_name = sys.argv[1]
    packs = find_similar_packages(pack_name)
    if len(packs) > 1:
        choices = ""
        for index, pack in enumerate(packs):
            choices += str(index + 1) + ": " + pack + "\n"
        pack_number = raw_input("Which package number do you really want?\n"
                                + choices)
        print("npm install " + packs[int(pack_number) - 1])
    else:
        print("npm install " + pack_name)
        """
    test_typos()

