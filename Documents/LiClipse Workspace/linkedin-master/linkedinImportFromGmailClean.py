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
from selenium.webdriver.common.keys import Keys
import glob
import os, errno
from selenium.webdriver.common.action_chains import ActionChains
from splitFileRandomly import splitFileRandomly



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
#             chromeOptions = webdriver.ChromeOptions()
#             prefs = {"profile.managed_default_content_settings.images":2}
#             chromeOptions.add_experimental_option("prefs",prefs)
# webdriver.Chrome(chrome_options=chromeOptions)
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

#         self.driver.close()

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

def get_password(website,username):
    """
    get password from stored keychain service
    """
    password = keyring.get_password(website, username)
    if not password:
        print("""You need to store password for this user
                                        first.""")
        print("Please enter the password for " + username)
        store_forget    (website,username)
        return get_password(website,username)

    return password

def store_forget(website,username):
    """
    Store given password for this username to keystore
    """
    passwd = getpass.getpass()
    keyring.set_password(website, username, passwd)
    click.echo("Password updated successfully")

def login_into_linkedin(driver, username):
    """
    Just login to linkedin if it is not already loggedin
    """
    userfield = driver.find_element_by_id('login-email')
    passfield = driver.find_element_by_id('login-password')
#     top = driver.find_element_by_css_selector('div.wrapper')
#     time.sleep(10)
    submit_form = driver.find_element_by_class_name('login-form')
#     driver.execute_script("return arguments[0].scrollIntoView();", top)
#     time.sleep(1000)
    password = get_password('linkedin',username)

    # If we have login page we get these fields
    # I know it's a hack but it works
    if userfield and passfield:
        userfield.send_keys(username)
        passfield.send_keys(password)
        submit_form.submit()
        click.echo("Logging in")
        
def login_into_gmail(driver, username):
    """
    Just login to linkedin if it is not already loggedin
    """
#     username = "jr991400@gmail.com"
#     username = "williamjh567@gmail.com"
    userfield = driver.find_element_by_id('identifierId')
    

    submit_form = driver.find_element_by_tag_name('form')

#     password = get_password(username)
    password = get_password('gmail',username)
#     password = "!@#$qwer1234"
    # If we have login page we get these fields
    # I know it's a hack but it works
    if userfield:
        userfield.send_keys(username)
        submit_form.submit()
        driver.find_element_by_id('identifierNext').click()
#         click.echo("Next")
#         raw_input("Press Enter to continue...")
        time.sleep(5)
        passfield = driver.find_element_by_name('password')
        passfield.send_keys(password)
        submit_form = driver.find_element_by_tag_name('form')
        driver.find_element_by_id('passwordNext').click()
        time.sleep(1)
        
        
def gmail_import_contacts(driver,filename):
    
    #         GO TO OLD IMPORT FOR CSV TO GMAIL
#     raw_input("Start import")
    time.sleep(5)
    driver.get('https://www.google.com/contacts/u/0/?cplus=0')
    time.sleep(5)
#     raw_input("Press Enter to continue...")
    driver.find_elements_by_css_selector('a.NMrsfe')[1].click()
#     raw_input("Press Enter to continue...")
    time.sleep(5)
    element = driver.find_element_by_name("file")
    
    element.send_keys(filename)
    driver.find_element_by_css_selector('button.VIpgJd-ldDVFe-zTETae').click()
#     raw_input("Finish Import...")
    time.sleep(5)
   
def gmail_delete_contactsFromLabel(driver,filename):
    driver.get('https://contacts.google.com/')
#     raw_input("Press Enter to continue...")
    time.sleep(5)
    labels = driver.find_elements_by_css_selector('div.jqJLq')
    
    for label in labels:
        try:
            labelhref = driver.find_element_by_css_selector('a.KIAioe').get_attribute('href')
            driver.get('https://www.google.com/contacts/u/0/?cplus=0')
            labelhref = labelhref.replace("./", "")
            driver.get(labelhref)
#             raw_input("Is it moving over?..")
            time.sleep(2)
            driver.find_element_by_css_selector('div.RANAid.jaWtS.GNgPAd').click()
            time.sleep(2)
#             raw_input("Press Enter to continue click on delete...")
            deleteSection = driver.find_elements_by_css_selector('div.fE4g1d')[1]
            print(deleteSection.get_attribute('innerHTML').encode('utf-8'))
            deleteSection.find_element_by_css_selector('div.zJKIV').click()
    #         print(deleteSection.find_elements_by_css_selector('div.zJKIV.i9xfbb')[1].get_attribute('innerHTML').encode('utf-8'))
#             raw_input("Press Enter to continue...")
            time.sleep(2)
            deleteButton = driver.find_element_by_css_selector('div.O0WRkf.oG5Srb.HQ8yf.C0oVfc.kHssdc.HvOprf.M9Bg4d').click()
        except:
            pass
            
        
        

        
        
def gmail_delete_contacts(driver,filename):
    driver.get('https://contacts.google.com/')
#     raw_input("Press Enter to continue...")
    time.sleep(5)
    firstContact = driver.find_elements_by_css_selector('div.XXcuqd')[0]
    firstContact.find_elements_by_css_selector("div[role='checkbox']")[0].click()
#     raw_input("Press Enter to continue...")
    time.sleep(5)
    
    BarContact = driver.find_elements_by_css_selector('div.H1IxX.qxFB7e')[0]
    BarContact.find_elements_by_css_selector("div[role='checkbox']")[0].click()
#     raw_input("Press Enter to continue...")
    time.sleep(5)
    BarContact.find_element_by_css_selector("div[aria-label='More actions']").click()
#     raw_input("Press Enter to continue...")
    time.sleep(5)
    driver.find_elements_by_css_selector("content[class='z80M1']")[1].click()
#     raw_input("Press Enter to continue...")
    time.sleep(5)
    driver.find_elements_by_css_selector("content[class='CwaK9']")[1].click()
#     raw_input("Press Enter to continue...")
    time.sleep(5)
    driver.find_element_by_css_selector("div[class='RANAid.jaWtS.GNgPAd']").click()
#     raw_input("Press Enter to continue...")
    time.sleep(5)
#     driver.find_elements_by_css_selector("content[class='CwaK9']")[1].click()
     
def scrapDataImportOnLinkedIn(bus,directory,basefilenameNoExt):
    url = 'https://www.linkedin.com/mynetwork/import-contacts/?transactionId=yzNLcH5VR9CZyvvt97F72g%3D%3D'
    bus.driver.get(url)
    time.sleep(2)
    #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
    bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
     
     
#     raw_input("scroll down.")
#     time.sleep(5)
    booleanWait =True
        
    while(booleanWait):
        try:
            bus.driver.find_element_by_css_selector('ul.mn-abi-results__nav-bar').location_once_scrolled_into_view                
            booleanWait = False
        except NoSuchElementException:
            time.sleep(1)
            pass
    
    prompt =0
    while prompt<100:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
    #                 file  = 'C:\Users\USUARIO\Documents\LiClipse Workspace\linkedin-master\emails\\' + name
    #                 result = bus.driver.get(url)
    #                 time.sleep(0.5)
     
     
    #                 bus.driver.find_element_by_css_selector("input.mn-abi-form__file-upload-input").clear()
    #                 time.sleep(2)
    #                 element = bus.driver.find_element_by_id("contacts-file-input")
    # #                 element.send_keys(file)
    # #                 bus.driver.find_element_by_css_selector('button.mn-abi-form__primary-btn').click()
    #                 time.sleep(20)
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.csv', 'w')    
    
    contactListHaveLI = []
    time.sleep(5)
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()
    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
    
    
    t0 = time.time()
    listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
    for people in listResults.find_elements_by_css_selector('li.mn-abi-result-card'):
        linkedInName = people.find_element_by_tag_name('h4').get_attribute('innerHTML')                  
        contactListHaveLI.append(linkedInName)
        
    t1= time.time() - t0
    print t1
         
    for i in contactListHaveLI:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')).strip())
        f.write('\n')
    #                 f.write('NEW EMAIL LIST')
    #                 f.write('\n')
    f.close()
    t2= time.time() - t1
    print t2
    
    
    
    
#     raw_input("click skip...")
#     time.sleep(5)
     
    bus.driver.find_element_by_id('add-all-connections').click()
     
#     raw_input("scroll down...")
    time.sleep(5)
    prompt =0
    while prompt<100:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
        
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()
    
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv', 'w') 
    
     
    contactListNotHaveLI = []
    listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
    for people in listResults.find_elements_by_tag_name('p'):
        peopleName = people.get_attribute('innerHTML')                  
        contactListNotHaveLI.append(peopleName)
    for i in contactListNotHaveLI:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')).strip())
        f.write('\n')
    #                 f.write('NEW EMAIL LIST')
    #                 f.write('\n')
    f.close()
    pass


def scrapDataImportOnLinkedInSourceFile(bus,directory,basefilenameNoExt):
    url = 'https://www.linkedin.com/mynetwork/import-contacts/?transactionId=yzNLcH5VR9CZyvvt97F72g%3D%3D'
    bus.driver.get(url)
    time.sleep(500)
    #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
    bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
     
     
#     raw_input("scroll down.")
#     time.sleep(5)
    booleanWait =True
        
    while(booleanWait):
        try:
            bus.driver.find_element_by_css_selector('ul.mn-abi-results__nav-bar').location_once_scrolled_into_view                
            booleanWait = False
        except NoSuchElementException:
            time.sleep(1)
            pass
    top = bus.driver.find_element_by_css_selector('div.mn-abi-results__takeover-header-content')
    
    
    prompt =0
    while prompt<100:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
    
    #                 file  = 'C:\Users\USUARIO\Documents\LiClipse Workspace\linkedin-master\emails\\' + name
    #                 result = bus.driver.get(url)
    #                 time.sleep(0.5)
     
     
    #                 bus.driver.find_element_by_css_selector("input.mn-abi-form__file-upload-input").clear()
    #                 time.sleep(2)
    #                 element = bus.driver.find_element_by_id("contacts-file-input")
    # #                 element.send_keys(file)
    # #                 bus.driver.find_element_by_css_selector('button.mn-abi-form__primary-btn').click()
    #                 time.sleep(20)
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
#     f = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.csv', 'w')    
    
    contactListHaveLI = []
    time.sleep(1)
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()
    
    bus.driver.execute_script("return arguments[0].scrollIntoView();", top)

    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
#     
#     
#     t0 = time.time()
#     listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
#     for people in listResults.find_elements_by_css_selector('li.mn-abi-result-card'):
#         linkedInName = people.find_element_by_tag_name('h4').get_attribute('innerHTML')                  
#         contactListHaveLI.append(linkedInName)
#         
#     t1= time.time() - t0
#     print t1
#          
#     for i in contactListHaveLI:
#         print i.encode('utf-8')
#         f.write(str(i.encode('utf-8')).strip())
#         f.write('\n')
#     #                 f.write('NEW EMAIL LIST')
#     #                 f.write('\n')
#     f.close()
#     t2= time.time() - t1
#     print t2
#     
#     
    
    
#     raw_input("click skip...")
    time.sleep(5)
     
    bus.driver.find_element_by_id('add-all-connections').click()
     
#     raw_input("scroll down...")
    time.sleep(2)
    prompt =0
    while prompt<200:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
        
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()

    
#     f = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv', 'w') 
    
#      
#     contactListNotHaveLI = []
#     listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
#     for people in listResults.find_elements_by_tag_name('p'):
#         peopleName = people.get_attribute('innerHTML')                  
#         contactListNotHaveLI.append(peopleName)
#     for i in contactListNotHaveLI:
#         print i.encode('utf-8')
#         f.write(str(i.encode('utf-8')).strip())
#         f.write('\n')
#     #                 f.write('NEW EMAIL LIST')
#     #                 f.write('\n')
#     f.close()
    pass

def scrapDataImportOnLinkedInSourceFileManual(bus,directory,basefilenameNoExt):
    url = 'https://www.linkedin.com/mynetwork/'
    bus.driver.get(url)
    time.sleep(2)
    #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
#     bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
     
     
    raw_input("Import and scroll")
#     time.sleep(5)
    booleanWait =True
        
#     while(booleanWait):
#         try:
#             bus.driver.find_element_by_css_selector('ul.mn-abi-results__nav-bar').location_once_scrolled_into_view                
#             booleanWait = False
#         except NoSuchElementException:
#             time.sleep(1)
#             pass
#     top = bus.driver.find_element_by_css_selector('div.mn-abi-results__takeover-header-content')
#     
#     
#     prompt =0
#     while prompt<100:
#         bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(0.1)
#         prompt +=1
    
    #                 file  = 'C:\Users\USUARIO\Documents\LiClipse Workspace\linkedin-master\emails\\' + name
    #                 result = bus.driver.get(url)
    #                 time.sleep(0.5)
     
     
    #                 bus.driver.find_element_by_css_selector("input.mn-abi-form__file-upload-input").clear()
    #                 time.sleep(2)
    #                 element = bus.driver.find_element_by_id("contacts-file-input")
    # #                 element.send_keys(file)
    # #                 bus.driver.find_element_by_css_selector('button.mn-abi-form__primary-btn').click()
    #                 time.sleep(20)
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
#     f = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.csv', 'w')    
    
    contactListHaveLI = []
    time.sleep(1)
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()
    
#     bus.driver.execute_script("return arguments[0].scrollIntoView();", top)

    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
#     
#     
#     t0 = time.time()
#     listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
#     for people in listResults.find_elements_by_css_selector('li.mn-abi-result-card'):
#         linkedInName = people.find_element_by_tag_name('h4').get_attribute('innerHTML')                  
#         contactListHaveLI.append(linkedInName)
#         
#     t1= time.time() - t0
#     print t1
#          
#     for i in contactListHaveLI:
#         print i.encode('utf-8')
#         f.write(str(i.encode('utf-8')).strip())
#         f.write('\n')
#     #                 f.write('NEW EMAIL LIST')
#     #                 f.write('\n')
#     f.close()
#     t2= time.time() - t1
#     print t2
#     
#     
    
    
    raw_input("click add and scroll down...")
#     time.sleep(5)
     
#     bus.driver.find_element_by_id('add-all-connections').click()
     
#     raw_input("scroll down...")
    time.sleep(2)
#     prompt =0
#     while prompt<200:
#         bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(0.1)
#         prompt +=1
        
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()

    
#     f = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv', 'w') 
    
#      
#     contactListNotHaveLI = []
#     listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
#     for people in listResults.find_elements_by_tag_name('p'):
#         peopleName = people.get_attribute('innerHTML')                  
#         contactListNotHaveLI.append(peopleName)
#     for i in contactListNotHaveLI:
#         print i.encode('utf-8')
#         f.write(str(i.encode('utf-8')).strip())
#         f.write('\n')
#     #                 f.write('NEW EMAIL LIST')
#     #                 f.write('\n')
#     f.close()
    pass

def scrapDataImportOnLinkedInManual(bus,directory,basefilenameNoExt):
    url = 'https://www.linkedin.com/mynetwork/'
    bus.driver.get(url)
    time.sleep(2)
    #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
#     bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
     
     
    raw_input("Import and scroll")
#     time.sleep(5)
    booleanWait =True
        
#     while(booleanWait):
#         try:
#             bus.driver.find_element_by_css_selector('ul.mn-abi-results__nav-bar').location_once_scrolled_into_view                
#             booleanWait = False
#         except NoSuchElementException:
#             time.sleep(1)
#             pass
#     top = bus.driver.find_element_by_css_selector('div.mn-abi-results__takeover-header-content')
#     
#     
#     prompt =0
#     while prompt<100:
#         bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(0.1)
#         prompt +=1
    
    #                 file  = 'C:\Users\USUARIO\Documents\LiClipse Workspace\linkedin-master\emails\\' + name
    #                 result = bus.driver.get(url)
    #                 time.sleep(0.5)
     
     
    #                 bus.driver.find_element_by_css_selector("input.mn-abi-form__file-upload-input").clear()
    #                 time.sleep(2)
    #                 element = bus.driver.find_element_by_id("contacts-file-input")
    # #                 element.send_keys(file)
    # #                 bus.driver.find_element_by_css_selector('button.mn-abi-form__primary-btn').click()
    #                 time.sleep(20)
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.csv', 'w')    
    
    contactListHaveLI = []
    time.sleep(1)
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()
    
#     bus.driver.execute_script("return arguments[0].scrollIntoView();", top)

    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
#     
#     
    t0 = time.time()
    listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
    for people in listResults.find_elements_by_css_selector('li.mn-abi-result-card'):
        linkedInName = people.find_element_by_tag_name('h4').get_attribute('innerHTML')
        linkedInFunction = people.find_element_by_tag_name('p').get_attribute('innerHTML') 
        peopleList = [linkedInName,linkedInFunction]              
        contactListHaveLI.append(peopleList)
         
    t1= time.time() - t0
    print t1
#          
    for j in contactListHaveLI:
        for i in j:
            print i.encode('utf-8')
            f.write(str(i.encode('utf-8')).strip() + ',')
        f.write('\n')
    #                 f.write('NEW EMAIL LIST')
    #                 f.write('\n')
    f.close()
    t2= time.time() - t1
    print t2
#     
#     
    
    
    raw_input("click add and scroll down...")
#     time.sleep(5)
     
#     bus.driver.find_element_by_id('add-all-connections').click()
     
#     raw_input("scroll down...")
    time.sleep(2)
#     prompt =0
#     while prompt<200:
#         bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(0.1)
#         prompt +=1
        
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()

    
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv', 'w') 
    
#      
    contactListNotHaveLI = []
    listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
    for people in listResults.find_elements_by_tag_name('p'):
        peopleName = people.get_attribute('innerHTML')                  
        contactListNotHaveLI.append(peopleName)
    for i in contactListNotHaveLI:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')).strip())
        f.write('\n')
#     #                 f.write('NEW EMAIL LIST')
#     #                 f.write('\n')
    f.close()
    pass


def scrapDataImportOnLinkedInSourceFileSkip(bus,directory,basefilenameNoExt):
    url = 'https://www.linkedin.com/mynetwork/import-contacts/?transactionId=yzNLcH5VR9CZyvvt97F72g%3D%3D'
    bus.driver.get(url)
    time.sleep(2)
    username = "jr991400@gmail.com" 
    #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
    bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
#     try:
#         bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
#     except NoSuchElementException:
#         email.driver.find_element_by_id("email").send_keys(username)
#         time.sleep(3)
#         driver.find_element_by_id('start-abi').click()
       
     
#     raw_input("scroll down.")
#     time.sleep(5)
    booleanWait =True
        
    while(booleanWait):
        try:
            bus.driver.find_element_by_css_selector('ul.mn-abi-results__nav-bar').location_once_scrolled_into_view                
            booleanWait = False
        except NoSuchElementException:
            time.sleep(1)
            pass
    top = bus.driver.find_element_by_css_selector('div.mn-abi-results__takeover-header-content')
    
    
    prompt =0
    while prompt<100:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
    
    #                 file  = 'C:\Users\USUARIO\Documents\LiClipse Workspace\linkedin-master\emails\\' + name
    #                 result = bus.driver.get(url)
    #                 time.sleep(0.5)
     
     
    #                 bus.driver.find_element_by_css_selector("input.mn-abi-form__file-upload-input").clear()
    #                 time.sleep(2)
    #                 element = bus.driver.find_element_by_id("contacts-file-input")
    # #                 element.send_keys(file)
    # #                 bus.driver.find_element_by_css_selector('button.mn-abi-form__primary-btn').click()
    #                 time.sleep(20)
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
#     f = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.csv', 'w')    
    
    contactListHaveLI = []
    time.sleep(1)
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()
    
    bus.driver.execute_script("return arguments[0].scrollIntoView();", top)

    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
#     
#     
#     t0 = time.time()
#     listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
#     for people in listResults.find_elements_by_css_selector('li.mn-abi-result-card'):
#         linkedInName = people.find_element_by_tag_name('h4').get_attribute('innerHTML')                  
#         contactListHaveLI.append(linkedInName)
#         
#     t1= time.time() - t0
#     print t1
#          
#     for i in contactListHaveLI:
#         print i.encode('utf-8')
#         f.write(str(i.encode('utf-8')).strip())
#         f.write('\n')
#     #                 f.write('NEW EMAIL LIST')
#     #                 f.write('\n')
#     f.close()
#     t2= time.time() - t1
#     print t2
#     
#     
    
    
#     raw_input("click skip...")
#     time.sleep(5)
     
    bus.driver.find_element_by_css_selector('button.button-secondary-medium-muted').click()
     
#     raw_input("scroll down...")
    time.sleep(2)
    prompt =0
    while prompt<200:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
        
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()

    
#     f = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv', 'w') 
    
#      
#     contactListNotHaveLI = []
#     listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
#     for people in listResults.find_elements_by_tag_name('p'):
#         peopleName = people.get_attribute('innerHTML')                  
#         contactListNotHaveLI.append(peopleName)
#     for i in contactListNotHaveLI:
#         print i.encode('utf-8')
#         f.write(str(i.encode('utf-8')).strip())
#         f.write('\n')
#     #                 f.write('NEW EMAIL LIST')
#     #                 f.write('\n')
#     f.close()
    pass


def scrapDataImportOnLinkedInNewScroll(bus,directory,basefilenameNoExt):
    url = 'https://www.linkedin.com/mynetwork/import-contacts/?transactionId=yzNLcH5VR9CZyvvt97F72g%3D%3D'
    bus.driver.get(url)
    time.sleep(2)
    #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
    bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
     
     
#     raw_input("scroll down.")
    
    booleanWait =True
        
    while(booleanWait):
        try:
            bus.driver.find_element_by_css_selector('ul.mn-abi-results__nav-bar').location_once_scrolled_into_view                
            booleanWait = False
        except NoSuchElementException:
            time.sleep(1)
            pass
    
    booleanScroll =True
        
    while(booleanScroll):
        try:
            bus.driver.find_element_by_css_selector('section.nav-footer-container__resources').location_once_scrolled_into_view
            time.sleep(0.2)
            bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            bus.driver.find_element_by_css_selector('section.nav-footer-container__resources').location_once_scrolled_into_view
            time.sleep(0.2)                
            booleanScroll = False
        except NoSuchElementException:
            bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)
            pass
    #                 file  = 'C:\Users\USUARIO\Documents\LiClipse Workspace\linkedin-master\emails\\' + name
    #                 result = bus.driver.get(url)
    #                 time.sleep(0.5)
     
     
    #                 bus.driver.find_element_by_css_selector("input.mn-abi-form__file-upload-input").clear()
    #                 time.sleep(2)
    #                 element = bus.driver.find_element_by_id("contacts-file-input")
    # #                 element.send_keys(file)
    # #                 bus.driver.find_element_by_css_selector('button.mn-abi-form__primary-btn').click()
    #                 time.sleep(20)
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.csv', 'w')    
    
    contactListHaveLI = []
    time.sleep(5)
    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
    listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
    for people in listResults.find_elements_by_css_selector('li.mn-abi-result-card'):
        linkedInName = people.find_element_by_tag_name('h4').get_attribute('innerHTML')                  
        contactListHaveLI.append(linkedInName)
         
    for i in contactListHaveLI:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')).strip())
        f.write('\n')
    #                 f.write('NEW EMAIL LIST')
    #                 f.write('\n')
    f.close()
     
#     raw_input("click skip...")
#     time.sleep(5)
     
    bus.driver.find_element_by_id('add-all-connections').click()
     
#     raw_input("scroll down...")
    time.sleep(5)
    booleanScroll =True
        
    while(booleanScroll):
        try:
            bus.driver.find_element_by_css_selector('section.nav-footer-container__resources').location_once_scrolled_into_view                
            booleanScroll = False
        except NoSuchElementException:
            bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)
            pass
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv', 'w') 
     
    contactListNotHaveLI = []
    listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
    for people in listResults.find_elements_by_tag_name('p'):
        peopleName = people.get_attribute('innerHTML')                  
        contactListNotHaveLI.append(peopleName)
    for i in contactListNotHaveLI:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')).strip())
        f.write('\n')
    #                 f.write('NEW EMAIL LIST')
    #                 f.write('\n')
    f.close()
    pass


def deleteImportedContacts(bus,directory,basefilenameNoExt):
    url = 'https://www.linkedin.com/mynetwork/contacts/imported/'
    bus.driver.get(url)
    time.sleep(2)
    #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
    bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
     
     
#     raw_input("scroll down.")
    time.sleep(5)
    
    prompt =0
    while prompt<200:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
        prompt +=1
    #                 file  = 'C:\Users\USUARIO\Documents\LiClipse Workspace\linkedin-master\emails\\' + name
    #                 result = bus.driver.get(url)
    #                 time.sleep(0.5)
     
     
    #                 bus.driver.find_element_by_css_selector("input.mn-abi-form__file-upload-input").clear()
    #                 time.sleep(2)
    #                 element = bus.driver.find_element_by_id("contacts-file-input")
    # #                 element.send_keys(file)
    # #                 bus.driver.find_element_by_css_selector('button.mn-abi-form__primary-btn').click()
    #                 time.sleep(20)
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.csv', 'w')    
    
    contactListHaveLI = []
    time.sleep(5)
    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
    listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
    for people in listResults.find_elements_by_css_selector('li.mn-abi-result-card'):
        linkedInName = people.find_element_by_tag_name('h4').get_attribute('innerHTML')                  
        contactListHaveLI.append(linkedInName)
         
    for i in contactListHaveLI:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')).strip())
        f.write('\n')
    #                 f.write('NEW EMAIL LIST')
    #                 f.write('\n')
    f.close()
     
#     raw_input("click skip...")
    time.sleep(5)
     
    bus.driver.find_element_by_id('add-all-connections').click()
     
#     raw_input("scroll down...")
    time.sleep(5)
    prompt =0
    while prompt<200:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
        prompt +=1
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv', 'w') 
     
    contactListNotHaveLI = []
    listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
    for people in listResults.find_elements_by_tag_name('p'):
        peopleName = people.get_attribute('innerHTML')                  
        contactListNotHaveLI.append(peopleName)
    for i in contactListNotHaveLI:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')).strip())
        f.write('\n')
    #                 f.write('NEW EMAIL LIST')
    #                 f.write('\n')
    f.close()
    pass

def scrapLinkedInAccountLink(bus,directory,basefilenameNoExt):
    
    
    prompt =0
    while prompt<200:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
    time.sleep(0)
    
    
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listLinkLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()
    
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listContact.csv', 'w')
       
    g = open(directory + '/treatment/'+ basefilenameNoExt +'/listContactFull.csv', 'w')
    contactListLink = []
    contactList = []
    
#     raw_input("Press Enter to go on to scrap linkedin Link")
    time.sleep(5)
    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
    for people in bus.driver.find_elements_by_css_selector('li.mn-person-card'):
        linkedInName = people.find_element_by_css_selector('span.mn-person-info__name').get_attribute('innerHTML')
        linkedInOccupation = people.find_element_by_css_selector('span.mn-person-info__occupation').get_attribute('innerHTML')
        linkedInLink = people.find_element_by_css_selector('a.mn-person-info__link').get_attribute('href')
        contact = [linkedInName,linkedInOccupation,linkedInLink]                  
        contactList.append(contact)                    
        contactListLink.append(linkedInLink)
        
    for i in contactListLink:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')))
        f.write('\n')
    f.close()
        
    for contactL in contactList:
        for i in contactL:
            print i.encode('utf-8')
            g.write(str(i.encode('utf-8')).strip() + ',')
        g.write('\n')
    g.close()

def scrapLinkedInAccountLinkSourceFile(bus,directory,basefilenameNoExt):
    newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
    bus.driver.get(newUrl)
    
    time.sleep(2)
    
    prompt =0
    while prompt<200:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
    time.sleep(0)
    
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        
    
    element = bus.driver.find_element_by_tag_name('body')     
    source_code = element.get_attribute('outerHTML')             
    sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listLinkLI.html', 'w')
    sour.write(source_code.encode('utf-8'))
    sour.close()
    

def scrapLinkedInAccountLinkSourceFileVersionWith100display(bus,directory,basefilenameNoExt):
    
    

    
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listContact.csv', 'w')
        
    g = open(directory + '/treatment/'+ basefilenameNoExt +'/listContactFull.csv', 'w')
    contactListLink = []
    contactList = []
    
#     raw_input("Press Enter to go on to scrap linkedin Link")
    time.sleep(0.5)
    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
    
        
    booleanMore = True
    i = 0
    
    while booleanMore:
        try :
            
            
            newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
            bus.driver.get(newUrl)
            time.sleep(1)
            checkbox = bus.driver.find_element_by_css_selector('label[for="contact-select-checkbox"]')
            checkbox.click()
            buttonWithdraw = bus.driver.find_element_by_css_selector('li.mn-list-toolbar__right-button')
            invit = bus.driver.find_elements_by_css_selector('li.mn-person-card')
            if(len(invit)==0):
                print('No more')
                booleanMore = False
            else:
                prompt =0
                while prompt<2:
                    bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.2)
                    prompt +=1
                time.sleep(0)
                
                element = bus.driver.find_element_by_css_selector('section.container-with-shadow')     
                source_code = element.get_attribute('outerHTML')             
                sour = open(directory + '/treatment/'+ basefilenameNoExt +'/listLinkLI'+str(i)+'.html', 'w')
                sour.write(source_code.encode('utf-8'))
                sour.close()
                i +=1
                for people in invit:
                    linkedInName = people.find_element_by_css_selector('span.mn-person-info__name').get_attribute('innerHTML')
                    linkedInOccupation = people.find_element_by_css_selector('span.mn-person-info__occupation').get_attribute('innerHTML')
                    linkedInLink = people.find_element_by_css_selector('a.mn-person-info__link').get_attribute('href')
                    contact = [linkedInName,linkedInOccupation,linkedInLink]                  
                    contactList.append(contact)                    
                    contactListLink.append(linkedInLink)
#                 raw_input("One loop?...")
                time.sleep(2)
                prompt =0
                while prompt<2:
                    bus.driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
                    time.sleep(0.2)
                    prompt +=1
    #             time.sleep(2)
    #             checkbox.click()
    #             time.sleep(2)
                time.sleep(0.5)
                buttonWithdraw.click()
                time.sleep(2)
                
        except NoSuchElementException:
            booleanDelete = False
            print('No hay')
        
        
    for i in contactListLink:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')))
        f.write('\n')
         
    for contactL in contactList:
        for i in contactL:
            print i.encode('utf-8')
            g.write(str(i.encode('utf-8')).strip() + ',')
        g.write('\n')
         
         
    f.close()
    g.close()
    
    
#     raw_input("Is that was correct?...")

    

    
    

def scrapLinkedInAccountLinkOneByOneAndDelete(bus,directory,basefilenameNoExt):
    newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
    bus.driver.get(newUrl)
    
    time.sleep(2)
    
    prompt =0
    while prompt<10:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        prompt +=1
    time.sleep(0)
    
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listContact.csv', 'w')
       
    g = open(directory + '/treatment/'+ basefilenameNoExt +'/listContactFull.csv', 'w')
    contactListLink = []
    contactList = []
    
#     raw_input("Press Enter to go on to scrap linkedin Link")
    time.sleep(5)
    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
    for people in bus.driver.find_elements_by_css_selector('li.mn-person-card'):
        linkedInName = people.find_element_by_css_selector('span.mn-person-info__name').get_attribute('innerHTML')
        linkedInOccupation = people.find_element_by_css_selector('span.mn-person-info__occupation').get_attribute('innerHTML')
        linkedInLink = people.find_element_by_css_selector('a.mn-person-info__link').get_attribute('href')
        contact = [linkedInName,linkedInOccupation,linkedInLink]                  
        contactList.append(contact)                    
        contactListLink.append(linkedInLink)
#         booleanDelete = True
#         while(booleanDelete):
#             try:
#                 people.find_element_by_css_selector("button[data-control-name='withdraw_single']").click()
#                 booleanDelete = False
#             except WebDriverException:
#                  booleanDelete = True
#             
#         time.sleep(0.5)
    
            
    for i in contactListLink:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')))
        f.write('\n')
    f.close()
        
    for contactL in contactList:
        for i in contactL:
            print i.encode('utf-8')
            g.write(str(i.encode('utf-8')).strip() + ',')
        g.write('\n')
    g.close()
    
    
    
       
def scrapLinkedInAccountLinkImportFile(bus,directory,basefilenameNoExt):
    
    

    
    try:
        os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    f = open(directory + '/treatment/'+ basefilenameNoExt +'/listContact.csv', 'w')
       
    g = open(directory + '/treatment/'+ basefilenameNoExt +'/listContactFull.csv', 'w')
    contactListLink = []
    contactList = []
    
#     raw_input("Press Enter to go on to scrap linkedin Link")
    time.sleep(0.5)
    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
    
    
        
    booleanMore = True
    i = 0
    while booleanMore:
        try :
            newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
            bus.driver.get(newUrl)
            
            time.sleep(1)
            checkbox = bus.driver.find_element_by_css_selector('label[for="contact-select-checkbox"]')
            checkbox.click()
            buttonWithdraw = bus.driver.find_element_by_css_selector('li.mn-list-toolbar__right-button')
            invit = bus.driver.find_elements_by_css_selector('li.mn-person-card')
            if(len(invit)==0):
                print('No more')
                booleanMore = False
            else:
                prompt =0
                while prompt<2:
                    bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.2)
                    prompt +=1
                time.sleep(0)
                for people in invit:
                    linkedInName = people.find_element_by_css_selector('span.mn-person-info__name').get_attribute('innerHTML')
                    linkedInOccupation = people.find_element_by_css_selector('span.mn-person-info__occupation').get_attribute('innerHTML')
                    linkedInLink = people.find_element_by_css_selector('a.mn-person-info__link').get_attribute('href')
                    contact = [linkedInName,linkedInOccupation,linkedInLink]                  
                    contactList.append(contact)                    
                    contactListLink.append(linkedInLink)
#                 raw_input("One loop?...")
                time.sleep(2)
                prompt =0
                while prompt<2:
                    bus.driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
                    time.sleep(0.2)
                    prompt +=1
    #             time.sleep(2)
    #             checkbox.click()
    #             time.sleep(2)
                time.sleep(0.5)
                buttonWithdraw.click()
                time.sleep(0.5)
                
        except NoSuchElementException:
            booleanDelete = False
            print('No hay')
        
        
    for i in contactListLink:
        print i.encode('utf-8')
        f.write(str(i.encode('utf-8')))
        f.write('\n')
        
    for contactL in contactList:
        for i in contactL:
            print i.encode('utf-8')
            g.write(str(i.encode('utf-8')).strip() + ',')
        g.write('\n')
        
        
    f.close()
    g.close()
    
    
#     raw_input("Is that was correct?...")

def removeImportedEmailLinkedIn(bus):
    newUrl = 'https://www.linkedin.com/mynetwork/contacts/imported/'
    bus.driver.get(newUrl)
    
    time.sleep(1)
    
    try:
        checkbox = bus.driver.find_element_by_css_selector('label[for="contact-select-checkbox"]')
#         checkbox = bus.driver.find_element_by_id('contact-select-checkbox')
        checkbox.click()
        time.sleep(0.5)
        
        buttonDelete = bus.driver.find_element_by_css_selector('button.mn-contacts__delete-selected-btn.button-secondary-medium.mv4')
        buttonDelete.click()   
        time.sleep(0.5)   
        buttonDeleteAll = bus.driver.find_element_by_css_selector('button.continue-action.button-primary-medium')
        buttonDeleteAll.click()   
        time.sleep(0.5)   
    except NoSuchElementException:
        print('No hay')
        pass

#     raw_input("Is that was correct?...")

def deleteLinkedInInvitations(bus):
    newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
    bus.driver.get(newUrl)
#     raw_input("Delete the invitations...")
    #                 time.sleep(5)
    booleanDelete = True
    i = 0
    while booleanDelete:
        try :
            print('Try find invitations')
            invit = bus.driver.find_elements_by_css_selector("button[data-control-name='withdraw_single']")
            if(len(invit)==0):
                print('No more')
                booleanDelete = False
            for invitation in invit:
                try:
                    invitation.click()
                    print('Delete')
                    i +=1
                    print(str(i))
                except NoSuchElementException:
                    pass
                except WebDriverException:
                    pass
                time.sleep(0.01)
        except NoSuchElementException:
            booleanDelete = False
            print('No hay')

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
@click.argument('scrapdirectory')
@click.argument('usergmail')
def crawl(browser, username, scrapdirectory, usergmail):
    """
    Run this crawler with specified username
    """

    # first check and read the input file
#     all_names = collect_names(inDirectory)
# 
#     fieldnames = ['fullname', 'locality', 'industry', 'current summary',
#                   'past summary', 'education', ]
#     # then check we can write the output file
#     # we don't want to complete process and show error about not
#     # able to write outputs
#     with open(outfile, 'w') as csvfile:
#         # just write headers now
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()

    link_title = './/a[@class="title main-headline"]'

    # now open the browser
    
    GMAIL_URL = "https://mail.google.com/"
    
#     with WebBus(browser) as busG:
# #         To log in
        
    
        
    with WebBus(browser) as bus:
        
        
#          
        bus.driver.get(GMAIL_URL)
        login_into_gmail(bus.driver, usergmail)
        time.sleep(2)
        raw_input("Go on to linked in...")
        bus.driver.get(LINKEDIN_URL)
        
#         raw_input("Press Enter to continue...")
        time.sleep(1)

  
        login_into_linkedin(bus.driver, username)
        raw_input("Go on to import contacts on google...")
        time.sleep(2)
        
        
#         path = "C:/Users/USUARIO/Documents/LiClipse Workspace/linkedin-master/listEmailsTreated/totreat2600/*.csv"
#         path = "C:/Users/USUARIO/Documents/LiClipse Workspace/linkedin-master/BekimList/2600/*.csv"
    
        path = scrapdirectory +"/2600/*.csv"
        
        for filename in glob.glob(path):
            print(filename)
            directory = os.path.dirname(filename)
            basefilename = os.path.basename(filename)
            filename = directory + "/" + basefilename
            print(filename)
            basefilenameNoExt = basefilename.replace(".csv", "")
#             raw_input("Delete contact from gmail...")
            removeImportedEmailLinkedIn(bus)
            removeImportedEmailLinkedIn(bus)
            gmail_delete_contactsFromLabel(bus.driver,filename)
            time.sleep(5)
            gmail_import_contacts(bus.driver,filename)
#             raw_input("get the contact into linkedin...")
            time.sleep(2)
        

            

#       edin.com/mynetwork/invitation-manager/sent/?filterCriteria=null']
        
            try:
                
                scrapDataImportOnLinkedInManual(bus,directory,basefilenameNoExt)

                raw_input("Import manually on LinkedIn...")
#                 time.sleep(5)
                
                newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
                bus.driver.get(newUrl)
    
                time.sleep(1)
                try:
#                     IF VERSION IS CHANGED
                    checkbox = bus.driver.find_element_by_css_selector('label[for="contact-select-checkbox"]')
                    scrapLinkedInAccountLinkSourceFileVersionWith100display(bus,directory,basefilenameNoExt)
                except NoSuchElementException:
#                                     ORIGINAL VERSION
                    scrapLinkedInAccountLink(bus,directory,basefilenameNoExt)
                    deleteLinkedInInvitations(bus)
                 
#                 scrapLinkedInAccountLinkOneByOneAndDelete(bus,directory,basefilenameNoExt)

                

#                 raw_input("Delete the invitations...")
#                 time.sleep(5)
                try:
                    os.makedirs(directory + '/treated/')
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                
                try :
                    os.rename(filename, directory + "/treated/" + basefilename)
                except WindowsError:
                    os.rename(filename, directory + "/treated/" + basefilename + 'Copy')
                    pass

#                 
#                 raw_input("Delete imported contact on linked in...")
#                 time.sleep(5)
#                 removeImportedEmailLinkedIn(bus)
#                 time.sleep(5)
#                 raw_input("Move file to treated...")
#                 scrapLinkedInAccountLinkImportFile(bus,directory,basefilenameNoExt)
         
#                    
# 
#                 newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
#                 bus.driver.get(newUrl)
#                 raw_input("Delete the invitations...")
# #                 time.sleep(5)
#                 booleanDelete = True
#                 i = 0
#                 while booleanDelete:
#                     try :
#                         print('Try find invitations')
#                         invit = bus.driver.find_elements_by_css_selector("button[data-control-name='withdraw_single']")
#                         if(len(invit)==0):
#                             print('No more')
#                             booleanDelete = False
#                         for invitation in invit:
#                             try:
#                                 invitation.click()
#                                 print('Delete')
#                                 i +=1
#                                 print(str(i))
#                             except NoSuchElementException:
#                                 pass
#                              
#                             time.sleep(0.01)
#                     except NoSuchElementException:
#                         booleanDelete = False
#                         print('No hay')
#                          
# #                 raw_input("Move file to treated...")
#                 time.sleep(5)
#                 
#                
                    

                
            except IndexError:
                continue
           

@click.command()
@click.option('--browser', default='phantomjs', help='Browser to run with')
@click.argument('username')
@click.argument('scrapdirectory')
def fetchaccountlink(browser, username, scrapdirectory):
    """
    Run this crawler with specified username
    """

    # first check and read the input file
#     all_names = collect_names(inDirectory)
# 
#     fieldnames = ['fullname', 'locality', 'industry', 'current summary',
#                   'past summary', 'education', ]
#     # then check we can write the output file
#     # we don't want to complete process and show error about not
#     # able to write outputs
#     with open(outfile, 'w') as csvfile:
#         # just write headers now
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()

    link_title = './/a[@class="title main-headline"]'

    # now open the browser
    

    
        
    with WebBus(browser) as bus:
        
        
        bus.driver.get(LINKEDIN_URL)
        
        time.sleep(1)

  
        login_into_linkedin(bus.driver, username)
        path = scrapdirectory +"/2600/missedAccountLink/id"
        
        try:
            f = open(path, 'r')
            id = int(f.readline().strip()) + 1
        except IOError:
            print("First time missing account")
            id=0
        basefilenameNoExt = str(id)
#       edin.com/mynetwork/invitation-manager/sent/?filterCriteria=null']
        
           
        newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
        bus.driver.get(newUrl)
    
        time.sleep(1)
        try:
#                  IF VERSION IS CHANGED
            checkbox = bus.driver.find_element_by_css_selector('label[for="contact-select-checkbox"]')
            scrapLinkedInAccountLinkSourceFileVersionWith100display(bus,directory,basefilenameNoExt)
        except NoSuchElementException:
#                                     ORIGINAL VERSION
            scrapLinkedInAccountLink(bus,directory,basefilenameNoExt)
            deleteLinkedInInvitations(bus)
      
          

@click.command()
@click.argument('website')
@click.argument('username')
def store(website,username):
    """
    Store given password for this username to keystore
    """
    passwd = getpass.getpass()
    keyring.set_password(website, username, passwd)
    click.echo("Password updated successfully")


cli.add_command(crawl)
cli.add_command(fetchaccountlink)
cli.add_command(store)

if __name__ == '__main__':
    cli()
