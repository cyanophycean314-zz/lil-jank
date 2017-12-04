import sys

def find_similar_packages(s):
    if s == "leftpda":
        return[s, "leftpad"]
    else:
        return[s]

if __name__ == "__main__":
    s = sys.argv[1]
    packs = find_similar_packages(s)
    if len(packs) > 1:
        choices = ""
        for index, pack in enumerate(packs):
            choices += str(index + 1) + ": " + pack + "\n"
        pack_number = raw_input("Which package number do you really want?\n"
                                + choices)
        print("npm install " + packs[int(pack_number) - 1])
    else:
        print("npm install " + s)

