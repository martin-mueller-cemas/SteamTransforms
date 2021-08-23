import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from MaltegoTransform import *

import config

MALTEGO = MaltegoTransform()

def output_to_maltego(name):
    last_name = name.split(' ',1)[-1].strip()
    first_name = name.replace(last_name, '').strip()
    person_entity = MALTEGO.addEntity("maltego.Person", name)
    person_entity.setType("maltego.Person")
    person_entity.addAdditionalFields("person.firstnames", "First Names", True, first_name)
    person_entity.addAdditionalFields("person.lastname", "Surname", True, last_name)


def extract_real_name(response):
    soup = BeautifulSoup(response, 'lxml')
    try:
        display_name = soup.select_one('bdi').getText()
        return display_name
    except AttributeError:
        MALTEGO.addUIMessage("No public profile")

def scrape_profile(url):
    ''' Returns DOM of profile URL'''

    options = Options()
    options.binary_location = config.FIREFOX_BINARY_PATH
    options.headless = True
    driver = webdriver.Firefox(executable_path=config.GECKODRIVER_BINARY_PATH, options=options)
    driver.get(url)
    element = driver.find_element_by_xpath('//*')
    html = element.get_attribute('innerHTML')
    return html

def output():
    MALTEGO.returnOutput()

def main():
    url = str(sys.argv[1])
    response = scrape_profile(url)
    name = extract_real_name(response)
    if name:
        output_to_maltego(name)
    output()

if __name__ == "__main__":
    main()