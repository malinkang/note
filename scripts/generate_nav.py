#!/usr/bin/python
# -*- coding: UTF-8 -*-
from genericpath import isdir
import os
files = [
    "nav.md",
    "./docs/android/README.md",
    "./docs/leetcode/README.md",
]

def read():
    nav = ""
    for file in files:
        with open(file, 'r') as f:
         nav+=f.read()
    return nav

def write():
    nav = read()
    with open("./mkdocs.yml", 'w') as f:
        f.write(nav)
if __name__ == "__main__":
    write()