import multiprocessing
import time
import os
import re
import string
import argparse

from colorama import Fore, Back, Style

pattern = re.compile("(?:[A-Za-z0-9\-\+=]{4}){4,}")


def calc_ratio(value, debug=False):
    uppercase = 0
    lowercase = 0
    number = 0
    symbols = 0
    total = 0
    for char in value:
        total += 1
        if char in string.ascii_uppercase:
            uppercase += 1
        elif char in string.ascii_lowercase:
            lowercase += 1
        elif char in string.digits:
            number += 1
        elif char in '-+=':
            symbols += 1

    lowercase_ratio = lowercase/total
    uppercase_ratio = uppercase/total
    number_ratio = number/total
    if debug:
        print(lowercase_ratio, uppercase_ratio, number_ratio, value[0:20])
    if lowercase_ratio >= 0.7:
        return False
    elif uppercase_ratio > 0.7:
        return False
    else:
        return True

def readfile(file, sensitivity=0):
    matches = []
    with open(file, 'r', encoding="utf8", errors='ignore') as fio:
        for l in fio.readlines():

            l = l.rstrip()
            m = pattern.findall(l)

            if m and calc_ratio(m[0], debug=False):
                l = l.replace(m[0], Fore.GREEN+m[0]+Style.RESET_ALL)
                matches.append(l)
            elif any([x in l.lower() for x in ['password', 'token', 'api-key', 'apikey', 'api_key']]) and sensitivity > 0:
                matches.append(f"Mention of password/token {l}")

    if len(matches) > 15:
        print(f"  Multiple matches in {file}")

    elif len(matches) > 0:
        print(f"  {file}")
        for m in matches:
            print(f"    {m}")


def search_dir(dir=None):
    pool = multiprocessing.Pool(processes=4)

    file_list = []
    disallowed_extensions = ['.webp', '.png', '.jpg', '.jpeg', '.apk', '.smali', '.dex', '.doc', '.xls', '.db']
    ignore_list = ['site-packages', '.git', 'htmlcov', 'requirements.txt']
    for root, dirs, files in os.walk(dir, topdown=True):
        for name in files:

            if not any([name.lower().endswith(ext) for ext in disallowed_extensions]):
                f_path = os.path.join(root, name)
                if not any([x in f_path for x in ignore_list]):
                    file_list.append(f_path)

    print(f"Files to search: {len(file_list)}")
    outputs = pool.map(readfile, file_list)

def search_file(filename):
    disallowed_extensions = ['.webp', '.png', '.jpg', '.jpeg', '.apk', '.smali', '.dex', '.doc', '.xls', '.db']
    ignore_list = ['site-packages', '.git', 'htmlcov', 'requirements.txt']
    if not any([name.lower().endswith(ext) for ext in disallowed_extensions]):
        f_path = os.path.join(filename)
        if not any([x in f_path for x in ignore_list]):
            file_list.append(f_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Secret Detective - find sensitive content in files")
    parser.add_argument('-d', help="The directory to search")
    parser.add_argument('-f', help="Search specific file")
    #parser.add_argument('--in-scope', help="File containing list of domains/subdomains that are in scope")

    args = parser.parse_args()
    if args.d:
        search_dir(dir=args.d)
    elif args.f:
        search_file(filename=args.f)

    #readfile("/home/brandon/git_repos/python_api/.env")
    print(Style.RESET_ALL)
