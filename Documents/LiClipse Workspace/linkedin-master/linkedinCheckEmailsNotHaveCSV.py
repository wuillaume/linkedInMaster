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
import os


LINKEDIN_URL = 'https://www.linkedin.com'


class UnknownUserException(Exception):
    pass


class UnknownBrowserException(Exception):
    pass





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


    
def crawl():
   
    numberFile = 2
                 
    rootdir = 'listEmailsTreated/externalData/traderXP.csv/2600/treated'
    
    listFiles = []
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filepath = os.path.join(subdir, file)
            basefilename = os.path.basename(filepath)
            basefilenameNoExt = basefilename.replace(".csv","")
            listFiles.append(basefilenameNoExt)
            print(basefilenameNoExt)
    
#     
#     with open('listEmailsTreated/robertemail.csv') as fileEmails:
#         fileEmails.readline()
#         linesEmails = fileEmails.readlines()
#     with open('listEmailsTreated/totreat2600/treatment/listNotHaveLI.csv') as fileHavenot:
#         linesNotHave = fileHavenot.readlines()
#         linesNotHave[:-1]
#       
#      
#     f = open('listEmailsTreated/ListForVicidialTotal.csv', 'w') 
#     g = open('listEmailsTreated/TableForVicidialTotal.csv', 'a')
# #              
#     for email in linesEmails:
#         booleanNotHave = False   
#         pNotHave = -1
#         for emailNot in linesNotHave:
#             pNotHave += 1
#     #             print(emailNot)
#             if(len(emailNot.split(','))>1):
#                 contact = emailNot.split(',')[1].strip()
#                 email = email.strip()
#                 if(email == contact):
#                     print(email)
#                     booleanNotHave = True
#                     del linesNotHave[pNotHave]
#         if(booleanNotHave == False):
#             f.write("'" +str(email) + "'" + ',')
#             g.write(str(email))
#             g.write('\n')
#     f.close()
#     g.close()
#     
#     exit

#     numberFileTotal = 3  
#     
    for basefilenameNoExt in listFiles:
        print(basefilenameNoExt)
        try:
            with open('listEmailsTreated/externalData/traderXP.csv/2600/treated/'+ basefilenameNoExt +'.csv') as fileEmails:
                fileEmails.readline()
                linesEmails = fileEmails.readlines()
                          
            with open('listEmailsTreated/externalData/traderXP.csv/2600/treatment/'+ basefilenameNoExt +'/listNotHaveLI.csv') as fileHavenot:
                linesNotHave = fileHavenot.readlines()
                linesNotHave[:-1]
                
            f = open('listEmailsTreated/externalData/traderXP.csv/2600/ForVicidial/ListForVicidial_'+ basefilenameNoExt +'.csv', 'w')
            fb = open('listEmailsTreated/externalData/traderXP.csv/2600/ForVicidial/TableForVicidial_'+ basefilenameNoExt +'.csv', 'w')
            g = open('listEmailsTreated/externalData/traderXP.csv/2600/ForVicidial/ListForVicidialTotal.csv', 'a')
            h = open('listEmailsTreated/externalData/traderXP.csv/2600/ForVicidial/TableForVicidialTotal.csv', 'a')
            print("GO")
            for email in linesEmails:
                email = email.replace(",","")
                if "'" not in email:
                    booleanNotHave = False   
                    pNotHave = -1
                    for emailNot in linesNotHave:
                        pNotHave += 1
            #             print(emailNot)
                        if(len(emailNot.split(','))>1):
                            contact = emailNot.split(',')[1].strip()
                        else:
                            contact = emailNot.strip()
                        email = email.strip()
        #                 print(email + "||" + contact + "||")
                        if(email == contact):
                            print(email)
                            booleanNotHave = True
                            del linesNotHave[pNotHave]
                    if(booleanNotHave == False):
                        f.write("'" +str(email).strip() + "'" + ',')
                        g.write("'" +str(email).strip() + "'" + ',')
                        h.write("'" +str(email).strip() + "'" + '\n')
                        fb.write("'" +str(email).strip() + "'" + '\n')
            f.close()
            g.close()
            h.close()
            fb.close()
        except:
            pass
        
#     numberFileTotal = 3  
#     
#     for numberFile in list(range(numberFileTotal)):
#         with open('listEmailsTreated/totreat2600/treated/emails'+ str(numberFile) +'.csv') as fileEmails:
#             fileEmails.readline()
#             linesEmails = fileEmails.readlines()
#                      
#         with open('listEmailsTreated/totreat2600/treatment/'+ str(numberFile) +'/listNotHaveLI.csv') as fileHavenot:
#             linesNotHave = fileHavenot.readlines()
#             linesNotHave[:-1]
#            
#         f = open('listEmailsTreated/totreat2600/ForVicidial/ListForVicidial_'+ str(numberFile) +'.csv', 'w')
#         g = open('listEmailsTreated/totreat2600/ForVicidial/TableForVicidialTotal.csv', 'a')
#              
#         for email in linesEmails:
#             booleanNotHave = False   
#             pNotHave = -1
#             for emailNot in linesNotHave:
#                 pNotHave += 1
#     #             print(emailNot)
#                 if(len(emailNot.split(','))>1):
#                     contact = emailNot.split(',')[1].strip()
#                     email = email.strip()
#                     if(email == contact):
#                         print(email)
#                         booleanNotHave = True
#                         del linesNotHave[pNotHave]
#             if(booleanNotHave == False):
#                 f.write("'" +str(email) + "'" + ',')
#                 g.write(str(email))
#                 g.write('\n')
#         f.close()
#         g.close()
#         
              
                    
                
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



if __name__ == '__main__':
    crawl()
