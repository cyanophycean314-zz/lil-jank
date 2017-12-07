
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
        l[i], l[j] = l[j], l[i]
    else:
        l[i] = c
    return ''.join(l)

def delete_char(s, i):
    assert len(s) > 0 and i in range(0, len(s))
    return s[:i] + s[i+1:]

def typo_generator(s):
    results = set()
    results.add(s)
    results.add(s.replace('-',''))
    results.add(s)

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
