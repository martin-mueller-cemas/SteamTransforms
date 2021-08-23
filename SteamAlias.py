#!/usr/bin/python3

import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from MaltegoTransform import *
import urllib.request, json

import config

MALTEGO = MaltegoTransform()

def output_to_maltego(alias):
    alias_entity = MALTEGO.addEntity("maltego.Alias", alias)
    alias_entity.setType("maltego.Alias") 

def extract_current_display_name(response):
    ''' Returns users current display name'''
    # If the user has only had one username then no aliases are displayed
    soup = BeautifulSoup(response, 'lxml')
    return soup.select_one('span.actual_persona_name').getText()

def scrape_profile(url):
    ''' Returns DOM of profile URL'''

    options = Options()
    options.binary_location = config.FIREFOX_BINARY_PATH
    options.headless = True
    driver = webdriver.Firefox(executable_path=config.GECKODRIVER_BINARY_PATH, firefox_options=options)
    driver.get(url)
    element = driver.find_element_by_xpath('//*')
    html = element.get_attribute('innerHTML')
    return html

def get_aliases_json(url):
    aliases = []
    json_url = url + "//ajaxaliases"
    with urllib.request.urlopen(json_url) as url:
        data = json.loads(url.read().decode())
    for entry in data:
        aliases.append(entry['newname'])
    return aliases


def output():
    MALTEGO.returnOutput()

def main():
    url = str(sys.argv[1])
    response = scrape_profile(url)
    aliases = []
    aliases.extend(get_aliases_json(url))
    if len(aliases) == 0:
        aliases.append(extract_current_display_name(response))
    for alias in aliases:
        output_to_maltego(alias)
    output()

if __name__ == "__main__":
    main()