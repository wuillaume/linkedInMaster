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
        
def login_into_gmail(driver, username):
    """
    Just login to linkedin if it is not already loggedin
    """
    username = "williamjh567@gmail.com"
    userfield = driver.find_element_by_id('identifierId')
    

    submit_form = driver.find_element_by_tag_name('form')

#     password = get_password(username)
    password = "!@#$qwer1234"
    # If we have login page we get these fields
    # I know it's a hack but it works
    if userfield:
        userfield.send_keys(username)
        submit_form.submit()
        driver.find_element_by_id('identifierNext').click()
#         click.echo("Next")
        raw_input("Press Enter to continue...")
#         time.sleep(5)
        passfield = driver.find_element_by_name('password')
        passfield.send_keys(password)
        submit_form = driver.find_element_by_tag_name('form')
        driver.find_element_by_id('passwordNext').click()
        time.sleep(1)
        
        
def gmail_import_contacts(driver,filename):
    
    #         GO TO OLD IMPORT FOR CSV TO GMAIL
    raw_input("Start import")
    driver.get('https://www.google.com/contacts/u/0/?cplus=0')
    raw_input("Press Enter to continue...")
    driver.find_elements_by_css_selector('a.NMrsfe')[1].click()
    raw_input("Press Enter to continue...")
    element = driver.find_element_by_name("file")
    
    element.send_keys(filename)
    driver.find_element_by_css_selector('button.VIpgJd-ldDVFe-zTETae').click()
    raw_input("Finish Import...")
        
def gmail_delete_contacts(driver,filename):
    driver.get('https://contacts.google.com/')
    raw_input("Press Enter to continue...")
    firstContact = driver.find_elements_by_css_selector('div.XXcuqd')[0]
    firstContact.find_elements_by_css_selector("div[role='checkbox']")[0].click()
    raw_input("Press Enter to continue...")
    
    BarContact = driver.find_elements_by_css_selector('div.H1IxX.qxFB7e')[0]
    BarContact.find_elements_by_css_selector("div[role='checkbox']")[0].click()
    raw_input("Press Enter to continue...")
    BarContact.find_element_by_css_selector("div[aria-label='More actions']").click()
    raw_input("Press Enter to continue...")
    driver.find_elements_by_css_selector("content[class='z80M1']")[1].click()
    raw_input("Press Enter to continue...")
    driver.find_elements_by_css_selector("content[class='CwaK9']")[1].click()
    raw_input("Press Enter to continue...")
    driver.find_element_by_css_selector("div[class='RANAid.jaWtS.GNgPAd']").click()
    raw_input("Press Enter to continue...")
#     driver.find_elements_by_css_selector("content[class='CwaK9']")[1].click()
     
def scrapDataImportOnLinkedIn(bus,directory,basefilenameNoExt):
    url = 'https://www.linkedin.com/mynetwork/import-contacts/?transactionId=yzNLcH5VR9CZyvvt97F72g%3D%3D'
    bus.driver.get(url)
    time.sleep(2)
    #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
    bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
     
     
    raw_input("scroll down.")
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
     
    raw_input("click skip...")
     
    bus.driver.find_element_by_id('add-all-connections').click()
     
    raw_input("scroll down...")
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
    newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
    bus.driver.get(newUrl)
    
    time.sleep(2)
    
    prompt =0
    while prompt<200:
        bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
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
    
    raw_input("Press Enter to go on to scrap linkedin Link")
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

    # first check and read the input file
    all_names = collect_names(infile)
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
        
        bus.driver.get(GMAIL_URL)
        login_into_gmail(bus.driver, username)
#         body = busG.driver.find_element_by_tag_name("body")
#         body.send_keys(Keys.CONTROL + 't')
#         busG.driver.get(LINKEDIN_URL)
        raw_input("Press Enter to continue...")
        

        path = "C:/Users/USUARIO/Documents/LiClipse Workspace/linkedin-master/listEmailsTreated/totreat2600/*.csv"
        
        for filename in glob.glob(path):
            print(filename)
            directory = os.path.dirname(filename)
            basefilename = os.path.basename(filename)
            filename = directory + "/" + basefilename
            print(filename)
            basefilenameNoExt = basefilename.replace(".csv", "")
#             os.rename(filename, directory + "/treated/" + basefilename)
            
#         filename = 'C://robdata.csv'
            gmail_import_contacts(bus.driver,filename)
            raw_input("Press Enter to continue...")
        
#         To log in
            bus.driver.get(LINKEDIN_URL)
        
            raw_input("Press Enter to continue...")
  
            login_into_linkedin(bus.driver, username)
        
            raw_input("Press Enter to continue...")
#         page = requests.get("https://www.linkedin.com/mynetwork/invitation-manager/sent/")
#  
#         
#         all_names = ['https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null']
        
            try:
                scrapDataImportOnLinkedIn(bus,directory,basefilenameNoExt)



#                 url = 'https://www.linkedin.com/mynetwork/import-contacts/?transactionId=yzNLcH5VR9CZyvvt97F72g%3D%3D'
#                 bus.driver.get(url)
#                 time.sleep(2)
# #                 bus.driver.find_element_by_css_selector('button.contacts-file-upload-btn').click()
#                 bus.driver.find_element_by_css_selector("li-icon[type='gmail-icon']").click()
#                 
#                 
#                 raw_input("scroll down.")
#                 prompt =0
#                 while prompt<200:
#                     bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                     time.sleep(0.2)
#                     prompt +=1
# #                 file  = 'C:\Users\USUARIO\Documents\LiClipse Workspace\linkedin-master\emails\\' + name
# #                 result = bus.driver.get(url)
# #                 time.sleep(0.5)
#                 
#                 
# #                 bus.driver.find_element_by_css_selector("input.mn-abi-form__file-upload-input").clear()
# #                 time.sleep(2)
# #                 element = bus.driver.find_element_by_id("contacts-file-input")
# # #                 element.send_keys(file)
# # #                 bus.driver.find_element_by_css_selector('button.mn-abi-form__primary-btn').click()
# #                 time.sleep(20)
#                 try:
#                     os.makedirs(directory + '/treatment/'+ basefilenameNoExt)
#                 except OSError as e:
#                     if e.errno != errno.EEXIST:
#                         raise
#                 f = open(directory + '/treatment/'+ basefilenameNoExt +'/listHaveLI.csv', 'w')    
# 
#                 contactListHaveLI = []
#                 time.sleep(5)
# #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
#                
#                 listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
#                 for people in listResults.find_elements_by_css_selector('li.mn-abi-result-card'):
#                     linkedInName = people.find_element_by_tag_name('h4').get_attribute('innerHTML')                  
#                     contactListHaveLI.append(linkedInName)
#                     
#                 for i in contactListHaveLI:
#                     print i.encode('utf-8')
#                     f.write(str(i.encode('utf-8')).strip())
#                     f.write('\n')
# #                 f.write('NEW EMAIL LIST')
# #                 f.write('\n')
#                 f.close()
#                 
#                 raw_input("click skip...")
#                 
# #                 bus.driver.find_element_by_id('add-all-connections').click()
#                 
#                 raw_input("scroll down...")
#                 prompt =0
#                 while prompt<200:
#                     bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                     time.sleep(0.2)
#                     prompt +=1
#                 f = open(directory + '/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv', 'w') 
#                 
#                 contactListNotHaveLI = []
#                 listResults = bus.driver.find_element_by_css_selector('ul.mn-abi-results__contacts-list')
#                 for people in listResults.find_elements_by_tag_name('p'):
#                     peopleName = people.get_attribute('innerHTML')                  
#                     contactListNotHaveLI.append(peopleName)
#                 for i in contactListNotHaveLI:
#                     print i.encode('utf-8')
#                     f.write(str(i.encode('utf-8')).strip())
#                     f.write('\n')
# #                 f.write('NEW EMAIL LIST')
# #                 f.write('\n')
#                 f.close()
                
                
#                 raw_input("Abort")
#                 
#                
#                 with open('emails/randEmail.csv') as f:
#                    lines = f.readlines()
#                 
#                 f = open('listEmailsTreated/toTreat2600/treatment/synthesis.csv', 'w') 
#                 
#                 pNotHave = 0
#                 pHave = 0
#                 
#                 for email in lines:
#                     contact = str(contactListNotHaveLI[pNotHave].encode('utf-8')).strip()
#                     print(email + '@@' + contact)
#                     if(email==contact):
#                         pNotHave += 1
#                         f.write(str(email) + ',Null')
#                         f.write('\n')
#                     else:
#                         try: 
#                             f.write(str(email) + ',' + str(contactListHaveLI[pHave].encode('utf-8')).strip())
#                         except:
#                             pass
#                         f.write('\n')
#                         pHave += 1
#                 f.write('NEW EMAIL LIST')
#                 f.write('\n')
#                 f.close()
                raw_input("Press Enter to continue...")
                
                scrapLinkedInAccountLink(bus,directory,basefilenameNoExt)
                
                raw_input("Delete the invitations...")
                
                newUrl = 'https://www.linkedin.com/mynetwork/invitation-manager/sent/?filterCriteria=null'
                bus.driver.get(newUrl)
                raw_input("Delete the invitations...")
                booleanDelete = True
                while booleanDelete:
                    try :
                        for invitation in bus.driver.find_elements_by_css_selector("button[data-control-name='withdraw_single']"):
                            invitation.click()
                            print('Delete')
                            time.sleep(0.5)
                    except NoSuchElementException:
                        booleanDelete = False
                        print('No hay')
                        
                raw_input("Move file to treated...")
                
                os.rename(filename, directory + "/treated/" + basefilename)
                    
                raw_input("Delete contact from gmail...")
                    
                gmail_delete_contacts(bus.driver,filename)
                
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
            except IndexError:
                continue
           

            
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
