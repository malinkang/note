#!/usr/bin/python
# -*- coding: UTF-8 -*-
from genericpath import isdir
import os
root = "./docs/leetcode"
result = " - "
for parent in os.listdir(root):
    child = os.path.join(root, parent)
    if(os.path.isdir(child)):
        for file in os.listdir(child):
            # print(file)
            if(file.endswith(".md") and file != "README.md"):
                with open(os.path.join(child, file), "r") as f:
                    title ="   - "+ f.readline().replace("#", "").strip()
                    title +=": "+os.path.join("leetcode/"+parent,file)
                    print(title)
            elif(file == "README.md"):
                with open(os.path.join(child, file), "r") as f:
                    title ="  - "+f.readline().replace("#", "").strip()
                    title +=": "
                    print(title)
