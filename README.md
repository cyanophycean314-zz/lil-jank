# Jank

Jank is a wrapper around npm, defending the user against typosquatting attacks and suspicious packages.

## Installation

The script will need packages python3 and python3-dateutil. On Debian-based systems, you can use

```
sudo apt install python3 python3-dateutil
```

Next, alias jank for ease of use.

```
alias jank="python3 jank.py"
```

Now you can install packages by typing

```
jank react
```

and be safe from typos. Yay!

---

By Kevin Fei, Nicholas Hasselmo, Jak Magaud