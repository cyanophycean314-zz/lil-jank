import subprocess, tarfile, json
import urllib.request 
from pprint import pprint

unsafe_keywords = ["http", "request", "process.env", "rm", \
"password", "username", "host", "network"]

def extract(tar_url, extract_path='.'):
    tar = tarfile.open(tar_url, 'r')
    for item in tar:
        tar.extract(item, extract_path)
        if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
            extract(item.name, "./" + item.name[:item.name.rfind('/')])

def check_script(script):
	if script == None:
		return False
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