# -*- coding: utf-8 -*-
"""
Simple Linkedin crawler to link email and name from a list downloaded

@author: idwaker

To use this you need linkedin account, all search is done through your account

Requirements:
    python-selenium
    python-click
    python-keyring

Tested on Python 3 not sure how Python 2 behaves
"""

import sys
import csv
import time
import click
import getpass
import keyring
from selenium import webdriver
from selenium.common.exceptions import (WebDriverException,
                                        NoSuchElementException)
from bs4 import BeautifulSoup
import string


LINKEDIN_URL = 'https://www.linkedin.com'


class UnknownUserException(Exception):
    pass


class UnknownBrowserException(Exception):
    pass


class WebBus:
    """
    context manager to handle webdriver part
    """

    def __init__(self, browser):
        self.browser = browser
        self.driver = None

    def __enter__(self):
        # XXX: This is not so elegant
        # should be written in better way
        if self.browser.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        elif self.browser.lower() == 'chrome':
            self.driver = webdriver.Chrome()
        elif self.browser.lower() == 'phantomjs':
            self.driver = webdriver.PhantomJS()
        else:
            raise UnknownBrowserException("Unknown Browser")

        return self

    def __exit__(self, _type, value, traceback):
        if _type is OSError or _type is WebDriverException:
            click.echo("Please make sure you have this browser")
            return False
        if _type is UnknownBrowserException:
            click.echo("Please use either Firefox, PhantomJS or Chrome")
            return False

        self.driver.close()

def encode(list):
    newList = []
    
    for item in list:
        itemEncode = item.encode('utf-8')
        newList.append(itemEncode)
        print itemEncode
        
    return newList

def get_password(username):
    """
    get password from stored keychain service
    """
    password = keyring.get_password('linkedinpy', username)
    if not password:
        raise UnknownUserException("""You need to store password for this user
                                        first.""")

    return password


def login_into_linkedin(driver, username):
    """
    Just login to linkedin if it is not already loggedin
    """
    userfield = driver.find_element_by_id('login-email')
    passfield = driver.find_element_by_id('login-password')

    submit_form = driver.find_element_by_class_name('login-form')

    password = get_password(username)

    # If we have login page we get these fields
    # I know it's a hack but it works
    if userfield and passfield:
        userfield.send_keys(username)
        passfield.send_keys(password)
        submit_form.submit()
        click.echo("Logging in")


def collect_names(filepath):
    """
    collect names from the file given
    """
    names = []
    with open(filepath, 'r') as _file:
        names = [line.strip() for line in _file.readlines()]
#     print names
    return names


@click.group()
def cli():
    """
    First store password

    $ python linkedin store username@example.com
    Password: **

    Then crawl linkedin for users

    $ python linkedin crawl username@example.com with_names output.csv --browser=firefox
    """
    pass


@click.command()
@click.option('--browser', default='phantomjs', help='Browser to run with')
@click.argument('username')
@click.argument('infile')
@click.argument('outfile')


    
def crawl(browser, username, infile, outfile):
    """
    Run this crawler with specified username
    """

                
    with open('listEmailsTreated/new1/listHaveLICol.csv') as fileHave:
        linesHave = fileHave.readlines()
                    
    with open('listEmailsTreated/new1/listNotHaveLICol.csv') as fileHavenot:
        linesNotHave = fileHavenot.readlines()
                    
               
    with open('listEmailsTreated/new1/randEmailScraped1000.csv') as f:
       lines = f.readlines()
                
    f = open('listEmailsTreated/new1/synthesis.csv', 'w') 
                
    pNotHave = 0
    pHave = 0
                
    for email in lines:
        contact = linesNotHave[pNotHave].strip()
        email = email.strip()
        print(email + '@@' + contact)
        if(email == contact):
            pNotHave += 1
            f.write(str(email) + ',Null')
            f.write('\n')
        else:
            try: 
                f.write(str(email) + ',' + linesHave[pHave].strip())
            except:
                pass
            f.write('\n')
            pHave += 1
    f.write('NEW EMAIL LIST')
    f.write('\n')
    f.close()
    raw_input("Press Enter to continue...")
                
                
              
                    
                
#                 element = bus.driver.find_element_by_tag_name('body')
#                 element = bus.driver.find_element_by_id('topcard') 
#                 result = result.get_attribute('outerHTML')
#                 source_code = element.get_attribute('outerHTML')
#                 soup = BeautifulSoup(source_code, 'html.parser')
#                
# #                 print(soup)
#                 
#                 for item in soup.findAll('div',{'role':'main'}):
#                     for item1 in item.findAll('h1',{ 'clas':'pv-top-card-section__name'}):
#                         print item1
#                 print result
                
#                 f = open('html_source_code.html', 'w')
#                  
#                 f.write(source_code.encode('utf-8'))
#                 f.close()
#       

            
#             
#             
# #            search_button = bus.driver.find_element_by_xpath(search_btn)
# #            search_button.click()
# 
#             profiles = []
# 
#             # collect all the profile links
#             results = None
#             try:
#                 results = bus.driver.find_element_by_id('results-container')
#             except NoSuchElementException:
#                 continue
#             links = results.find_elements_by_xpath(link_title)
# 
#             # get all the links before going through each page
#             links = [link.get_attribute('href') for link in links]
#             for link in links:
#                 # XXX: This whole section should be separated from this method
#                 # XXX: move try-except to context managers
#                 bus.driver.get(link)
# 
#                 overview = None
#                 overview_xpath = '//div[@class="profile-overview-content"]'
#                 try:
#                     overview = bus.driver.find_element_by_xpath(overview_xpath)
#                 except NoSuchElementException:
#                     click.echo("No overview section skipping this user")
#                     continue
# 
#                 # every xpath below here are relative
#                 fullname = None
#                 fullname_xpath = './/span[@class="full-name"]'
#                 try:
#                     fullname = overview.find_element_by_xpath(fullname_xpath)
#                 except NoSuchElementException:
#                     # we store empty fullname : notsure for this
#                     fullname = ''
#                 else:
#                     fullname = fullname.text.strip()
# 
#                 locality = None
#                 try:
#                     locality = overview.find_element_by_class_name('locality')
#                 except NoSuchElementException:
#                     locality = ''
#                 else:
#                     locality = locality.text.strip()
# 
#                 industry = None
#                 try:
#                     industry = overview.find_element_by_class_name('industry')
#                 except NoSuchElementException:
#                     industry = ''
#                 else:
#                     industry = industry.text.strip()
# 
#                 current_summary = None
#                 csummary_xpath = './/tr[@id="overview-summary-current"]/td'
#                 try:
#                     current_summary = overview.find_element_by_xpath(csummary_xpath)
#                 except NoSuchElementException:
#                     current_summary = ''
#                 else:
#                     current_summary = current_summary.text.strip()
# 
#                 past_summary = None
#                 psummary_xpath = './/tr[@id="overview-summary-past"]/td'
#                 try:
#                     past_summary = overview.find_element_by_xpath(psummary_xpath)
#                 except NoSuchElementException:
#                     past_summary = ''
#                 else:
#                     past_summary = past_summary.text.strip()
# 
#                 education = None
#                 education_xpath = './/tr[@id="overview-summary-education"]/td'
#                 try:
#                     education = overview.find_element_by_xpath(education_xpath)
#                 except NoSuchElementException:
#                     education = ''
#                 else:
#                     education = education.text.strip()
# 
#                 data = {
#                     'fullname': fullname,
#                     'locality': locality,
#                     'industry': industry,
#                     'current summary': current_summary,
#                     'past summary': past_summary,
#                     'education': education,
#                 }
#                 profiles.append(data)
# 
#             with open(outfile, 'a+') as csvfile:
#                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#                 writer.writerows(profiles)
# 
#             click.echo("Obtained ..." + name)


@click.command()
@click.argument('username')
def store(username):
    """
    Store given password for this username to keystore
    """
    passwd = getpass.getpass()
    keyring.set_password('linkedinpy', username, passwd)
    click.echo("Password updated successfully")


cli.add_command(crawl)
cli.add_command(store)


if __name__ == '__main__':
    cli()
