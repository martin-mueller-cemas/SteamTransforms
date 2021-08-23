#!/usr/bin/python3

import sys
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from MaltegoTransform import *
from random import shuffle

import config

MALTEGO = MaltegoTransform()

def output_to_maltego(display_name, url, img_url):
    ''' Adds maltego entities from url '''

    split_url = url.split('/')
    profile_id = split_url[-1]
    web_entity = MALTEGO.addEntity("WindyMiller.SteamAccount", url)
    web_entity.setType("WindyMiller.SteamAccount")
    web_entity.addAdditionalFields("url", "URL", True, url)
    web_entity.addAdditionalFields("title", "Title", True, profile_id)
    web_entity.addAdditionalFields("short-title", "Short Title", True, display_name)
    web_entity.setIconURL(img_url)

def extract_friends_list(response):
    soup = BeautifulSoup(response, 'lxml')
    friends = []
    for friend in soup.select('div.friendBlock'):
        friend_block = friend.select_one('div.friendBlockContent').getText()
        #Get names of offline users
        friend_block_split = friend_block.split('Last Online')
        friend_block = friend_block_split[0].strip()
        #Get names of online users
        friend_block_split = friend_block.split('\t\tOnline')
        friend_block = friend_block_split[0].strip()
        #Get names of users playing game
        friend_block_split = friend_block.split('In-Game')
        friend_block = friend_block_split[0].strip()
        #Get names of users playing non-steam game
        friend_block_split = friend_block.split('In non-Steam')
        friend_block = friend_block_split[0].strip()
        friends.append(friend_block)
    return friends

def extract_friends_profiles_url(response):
    soup = BeautifulSoup(response, 'lxml')
    urls = []
    for friend in soup.select('div.friendBlock'):
        urls.append(friend.select_one('a.friendBlockLinkOverlay').get('href'))
    return urls

def extract_profile_img_url(response):
    soup = BeautifulSoup(response, 'lxml')
    urls = []
    for friend in soup.select('div.friendBlock'):
        urls.append(friend.select_one('div.playerAvatar > img').get('src'))
    return urls

def scrape_profile(url):
    ''' Returns DOM of profile URL'''
    friends_url = url + "//friends/"
    options = Options()
    options.binary_location = config.FIREFOX_BINARY_PATH
    options.headless = True
    driver = webdriver.Firefox(executable_path=config.GECKODRIVER_BINARY_PATH, options=options)
    driver.get(friends_url)
    element = driver.find_element_by_xpath('//*')
    html = element.get_attribute('innerHTML')
    return html

def output():
    MALTEGO.returnOutput()

def main():
    url = str(sys.argv[1])
    response = scrape_profile(url)
    friends_list = extract_friends_list(response)
    url_list = extract_friends_profiles_url(response)
    img_url_list = extract_profile_img_url(response)
    friends = []
    if len(friends_list) > 0:
        for friend, url, img_url in zip(friends_list, url_list, img_url_list):
            friends.append({'display_name': friend, 'url': url, 'img_url': img_url})
        shuffle(friends)
        for friend in friends:
            output_to_maltego(friend['display_name'], friend['url'],friend['img_url'])
    output()


if __name__ == "__main__":
    main()