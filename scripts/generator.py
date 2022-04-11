#!/usr/bin/python
# -*- coding: UTF-8 -*-
from multiprocessing import parent_process
import os
import pathlib
from pydoc_data.topics import topics
import requests
import argparse

from requests.api import get, post

# 获取内容

root = "./docs"
parent = ""


def retrieve_block_children(id):
    r = requests.get('https://api.notion.com/v1/blocks/' +
                     id+'/children', headers=headers)
    return r


def retrieve_a_database(id):
    r = requests.get("https://api.notion.com/v1/databases/" +
                     id, headers=headers)
    json = r.json()
    title = json.get("title")[0].get("text").get("content")
    title = title.lower()
    toc = "  - "+title+":\n"
    parent = root+"/"+title
    pathlib.Path(parent).mkdir(parents=True, exist_ok=True)
    print(title)
    options = json.get("properties").get("Tag").get("select").get("options")
    for option in options:
        tag = option.get("name")
        dir = title+"/"+tag.lower()
        print(dir)
        pathlib.Path(root+"/"+dir).mkdir(parents=True, exist_ok=True)
        toc += query_a_database(id, dir, tag)
    # 写入目录
    write_to_file(toc, parent+"/README.md")


def query_a_database(id, dir, tag):
    toc = "    - "+tag+":\n"
    body = {
        "filter": {"and": [
            {"property": "File", "rich_text": {"is_not_empty": True}},
            {"property": "Tag", "select": {"equals": tag}},
        ]}
    }
    r = requests.post(
        "https://api.notion.com/v1/databases/"+id+"/query",
        headers=headers,
        json=body,
    )
    results = r.json().get("results")
    if(results is not None):
        for result in r.json().get("results"):
            id = result.get("id")
            properties = result.get("properties")
            title = properties.get("Title").get(
                "title")[0].get("text").get("content")
            print(title)
            tag = properties.get("Tag").get("select").get("name")
            file = properties.get("File").get("rich_text")[
                0].get("text").get("content")
            file = dir+"/"+file+".md"
            toc += "      - "+title+": "+file+"\n"
            markdown = parse_content(id)
            file = root+"/"+file
            write_to_file(markdown, file)
    print(toc)
    return toc


def write_to_file(content, file):
    with open(file, "w") as f:
        f.seek(0)
        f.write(content)
        f.truncate()

# 解析文本


def parse_format(text):
    r = ''
    for t in text:
        content = t.get("text").get("content")
        link = t.get("text").get("link")
        if(not link is None):
            url = link.get("url")
            content = "["+content+"]("+url+")"
        annotations = t.get("annotations")
        bold = annotations.get("bold")
        italic = annotations.get("italic")
        strikethrough = annotations.get("strikethrough")
        underline = annotations.get("underline")
        code = annotations.get("code")
        color = annotations.get("color")
        if(bold):
            content = "**"+content+"**"
        if(italic):
            content = "_"+content+"_"
        if(strikethrough):
            content = "~~"+content+"~~"
        if(underline):
            content = "<u>"+content+"</u>"
        if(code):
            content = "`"+content+"`"
        if(color != 'default'):
            content = "<font color='"+color+"'>"+content+"</font>"
        r += content
    return r


def parse_content(id):
    markdown = ""
    r = retrieve_block_children(id)
    print(r.text)
    results = r.json().get("results")
    for result in results:
        type = result.get("type")
        text = result.get(type).get("text")
        if(not text is None):
            # text是一个数组 如果text长度为0 说明是回车
            if(len(text) > 0):
                content = parse_format(text)
                if(type == "heading_1"):
                    markdown += "# " + content + "\n\n"
                elif(type == "heading_2"):
                    markdown += "\n## "+content+"\n\n"
                elif(type == "heading_3"):
                    markdown += "\n### "+content+"\n\n"
                elif(type == "to_do"):
                    markdown += "- [x] "+content+"\n\n"
                elif(type == "bulleted_list_item"):
                    markdown += "* "+content+"\n\n"
                elif(type == "paragraph"):
                    markdown += content+"\n\n"
                elif(type == "code"):
                    language = result.get(type).get("language")
                    if(language == "plain text"):
                        markdown += "```\n"+content+"\n```\n\n"
                    else:
                        markdown += "```"+language+"\n"+content+"\n```\n\n"
            else:
                markdown += "\n"
        elif(type == "image"):
            external = result.get(type).get("external")
            file = result.get(type).get("file")
            if(not external is None):
                url = external.get("url")
            elif(not file is None):
                url = file.get("url")
            markdown += "![]("+url+")\n"
    return markdown


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("secret")
    parser.add_argument("version")
    parser.add_argument("id")
    options = parser.parse_args()
    headers = {'Authorization': options.secret,
               "Notion-Version": options.version}
    retrieve_a_database(options.id)
