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
import glob
import os
import difflib



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
@click.argument('scrapdirectory')


    
def crawl(scrapdirectory):
    """
    Run this crawler with specified username
    """
    

    path = scrapdirectory +"/2600/ForVicidial/TableForVicidial_*.csv"
    
    fullVicidial = open(scrapdirectory +'/list_vicidial.csv' , 'r')
    line = fullVicidial.readline()
    lineArray = line.split(",")
    p=0
    iFirstName = -1
    iLastName = -1
    iEmail = -1
    for item in lineArray:
        if(item=="first_name"):
            iFirstName = p
        if(item=="last_name"):
            iLastName = p
        if(item=="email"):
            iEmail = p
        p +=1
    
    print(iFirstName)
    print(iLastName)
    print(iEmail    )
    
    g = open(scrapdirectory +'/2600/treatment/matchVicidialLinkedIn.csv', 'w') 
    for filename in glob.glob(path):
        directory = os.path.dirname(filename)
        basefilename = os.path.basename(filename)
        filename = directory + "/" + basefilename
        print(filename)
        basefilenameNoExt = basefilename.replace(".csv", "")
        basefilenameNoExt = basefilenameNoExt.replace("TableForVicidial_", "")
        
        fileEmails=open(filename,'r')
        emailHaves = fileEmails.readlines()
        f = open(scrapdirectory +'/2600/treatment/'+basefilenameNoExt+'/matchVicidialLinkedIn.csv', 'w') 
        
        for emailhave in emailHaves:
            fullVicidial = open(scrapdirectory +'/list_vicidial.csv' , 'r')
            line = fullVicidial.readline()
            emailhave = emailhave.replace("'", "")
            notFound=True
            while(notFound):
                 line = fullVicidial.readline()
#                  print(line)
                 lineArray = line.split(",")
                 email = lineArray[iEmail]
#                  print(emailhave.strip()+"||"+email.strip()+"||")
                 if(emailhave.strip() == email.strip()):
                    print(emailhave.strip()+"||"+email.strip()+"||")

                    with open(scrapdirectory +'/2600/treatment/'+basefilenameNoExt+'/listContactFull.csv') as fileContact:
                        linesContact = fileContact.readlines()
                    similMax =0
                    lineContact = ""
                    for contact in linesContact:
                        contactArray = contact.split(",")
                        name = contactArray[0]
                        nameVicidial = lineArray[iFirstName]+' '+lineArray[iLastName]
                        simil = difflib.SequenceMatcher(None, name, nameVicidial).ratio()
                        if(simil>similMax):
                            similMax=simil
                            lineContact = line.strip()+","+name.strip()+","+contactArray[-2].strip()+","+str(simil)
                    if(similMax>0):
                        f.write(lineContact)
                        f.write('\n')
                        g.write(lineContact)
                        g.write('\n')
                        notFound=False
                        
        f.close()
        raw_input("Press Enter to continue...")
    g.close()           
                
              


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
