# -*- coding: utf-8 -*-
"""
Simple Linkedin scraper to collect user's  profile data.

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
from selenium.webdriver.common.action_chains import ActionChains
from random import randint
from test.sortperf import randfloats
import os, errno
from selenium.webdriver.common.keys import Keys


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


def collect_link(filepath):
    """
    collect names from the file given
    """
    link = []
    with open(filepath, 'r') as _file:
        link = [line.strip() for line in _file.readlines()]
    print link
    return link


@click.group()
def cli():
    """
    First store password

    $ python linkedin store username@example.com
    Password: **

    Then scrap linkedin for users

    $ python linkedin scrap username@example.com with_names output.csv --browser=firefox
    """
    pass


@click.command()
@click.option('--browser', default='phantomjs', help='Browser to run with')
@click.argument('username')
@click.argument('infile')


    
def scrap(browser, username, infile):
    
    directoryToSave = 'BekimList/fullProfile/scrapFiles'
    
#     f = open(directoryToSave+'/id', 'r')
#     string_lead_id = f.read()
# #     print string_lead_id
#     lead_id = int(string_lead_id)
#     f.close()
#     print lead_id
    """
    Run this scraper with specified username
    """

    # first check and read the input file
    all_linkedInProfile = collect_link(infile)

#     fieldnames = ['fullname', 'locality', 'industry', 'current summary',
#                   'past summary', 'education', ]
#     # then check we can write the output file
#     # we don't want to complete process and show error about not
#     # able to write outputs
#     with open(outfile, 'a') as csvfile:
#         # just write headers now
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()

    link_title = './/a[@class="title main-headline"]'

    # now open the browser
    with WebBus(browser) as bus:
#         To log in
        bus.driver.get(LINKEDIN_URL)
#     
        login_into_linkedin(bus.driver, username)
        
        raw_input("Press Enter to continue...")
#         page = requests.get("https://www.linkedin.com/mynetwork/invitation-manager/sent/")
#  
#         

        for link in all_linkedInProfile:
            
            try:
                try:
                    os.makedirs(directoryToSave + '/full_source/')
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                print link
                link = link.split(",")
                lead_id = link[0]
                url = link[1]
                print url
                f = open(directoryToSave+'/id', 'r')
                string_lead_id = f.read()
                f.close()
                listLeadID = string_lead_id.split(",")
                booleanNotDone = True
                for lead in listLeadID:
                    if(lead_id==lead):
                        booleanNotDone = False
                if(booleanNotDone):
                    print url
                    
#                     time.sleep(randint(1,6))
#                     scroll = randint(0,400)
#                     bus.driver.execute_script("window.scrollTo(0, scroll);")
#                     
#                     navMain = bus.driver.find_element_by_css_selector('ul.nav-main')
#                     for item in navMain.find_elements_by_css_selector('li.nav-item'):
#                         if (randint(0,10)>7):                       
#                             item.find_element_by_css_selector('a.nav-item__link').click()
#                             time.sleep(randint(4,12))
#                    
    #                 time.sleep(2)
                    
                    result = bus.driver.get(url)
                    time.sleep(2)
                    try :
                        bus.driver.find_element_by_css_selector('button.contact-see-more-less').click()
                        time.sleep(0.5)
                    except NoSuchElementException:
                        pass
    #                 
                    footer = bus.driver.find_element_by_css_selector("div.nav-footer")
    #                 print(footer.get_attribute('innerHTML').encode('utf-8'))
    #                 bus.driver.execute_script("arguments[0].scrollIntoView(true);", footer)
                    booleanScroll = True
                    builder = ActionChains(bus.driver)
                    while booleanScroll:
                        try :
                            builder.move_to_element(footer).perform()
                            booleanScroll = False
                        except:
                            bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(0.5)
                            pass
                    
                    time.sleep(2)
                    
                   
                    
                    
                    
    #                 soup = BeautifulSoup(source_code, 'html.parser')
    #                
    # #                 print(soup)
    #                 
    #                 for item in soup.findAll('div',{'role':'main'}):
    #                     for item1 in item.findAll('h1',{ 'clas':'pv-top-card-section__name'}):
    #                         print item1
    #                 print result
    
    
                    
                    full_name ='NULL'
                    headline ='NULL'
                    company ='NULL'
                    school ='NULL'
                    location ='NULL'
                    number_connections ='NULL'
                    summary_text ='NULL'
                    linkedInName ='NULL'
                    linkedInLink ='NULL'
                    twitterName ='NULL'
                    twitterLink ='NULL'
                    premium ='NULL'
                    
                    
                    try:
                        premium = bus.driver.find_element_by_css_selector('a.pv-member-badge__premium-upsell').get_attribute('innerHTML')
                        print(premium.encode('utf-8'))
                    except NoSuchElementException:
                        pass
                    try : 
                        full_name = bus.driver.find_element_by_class_name('pv-top-card-section__name').get_attribute('innerHTML')
                        print(full_name.encode('utf-8'))
                    except NoSuchElementException:
                        pass
                    try :
                        headline = bus.driver.find_element_by_class_name('pv-top-card-section__headline').get_attribute('innerHTML')
                        print(headline.encode('utf-8'))
                    except NoSuchElementException:
                        pass
                    try :
                        company = bus.driver.find_element_by_class_name('pv-top-card-section__company').get_attribute('innerHTML')
                        print(company.encode('utf-8'))
                    except NoSuchElementException:
                        pass
                    try :
                        school = bus.driver.find_element_by_class_name('pv-top-card-section__school').get_attribute('innerHTML')
                        print(school.encode('utf-8'))
                    except NoSuchElementException:
                        pass
                    try :
                        location = bus.driver.find_element_by_class_name('pv-top-card-section__location').get_attribute('innerHTML')
                        print(location.encode('utf-8'))
                    except NoSuchElementException:
                        pass
                    number_connections = bus.driver.find_element_by_class_name('pv-top-card-section__connections').find_elements_by_tag_name('span')[0].get_attribute('innerHTML')
                    print(number_connections.encode('utf-8'))
                    try :
                        summary_text = bus.driver.find_element_by_css_selector('span.truncate-multiline--last-line-wrapper').find_elements_by_tag_name('span')[0].get_attribute('innerHTML')
                    except NoSuchElementException:
                        pass
                    print(summary_text.encode('utf-8'))
                    
                    try :
                        linkedin= bus.driver.find_element_by_css_selector('section.ci-vanity-url')
                        print(linkedin.get_attribute('innerHTML').encode('utf-8'))
                        linkedInName = linkedin.find_element_by_css_selector('a.pv-contact-info__contact-link').get_attribute('innerHTML')
                        linkedInLink = linkedin.find_element_by_css_selector('a.pv-contact-info__contact-link').get_attribute('href')
                    except NoSuchElementException:
                        pass
                    
                    print linkedInName.encode('utf-8')
    #                 f.write(str(linkedInName.encode('utf-8')))
    #                 f.write(str(linkedInLink.encode('utf-8')))
                    try :
                        twitter= bus.driver.find_element_by_css_selector('section.ci-twitter')
                        twitterName = twitter.find_element_by_css_selector('a.pv-contact-info__contact-link').get_attribute('innerHTML')
                        twitterLink = twitter.find_element_by_css_selector('a.pv-contact-info__contact-link').get_attribute('href')
                    except NoSuchElementException:
                        pass
                    
                    
    #                 print twitterName.encode('utf-8')
    #                 f.write(str(twitterName))
    #                 f.write(str(twitterLink))
                    
                    basic_info = [full_name,headline,company,school,location,number_connections,summary_text,linkedInName,linkedInLink,twitterName,twitterLink,premium]
                    
                    f = open(directoryToSave+'/basic_info.csv', 'a')
                    
                    f.write('"' + str(lead_id) + '",')
                    
                    for info in basic_info:
                        string = '"' + str(info.encode('utf-8')).strip() + '",'
                        
                        f.write(string)
                    f.write('\n')
                    f.close()
                    
                    
                    ## FOR THE EXPERIENCE
                    experienceList = []
                    
                    
    #                 for work in bus.driver.find_elements_by_class_name('experience-section'):
                    try :
                        exp = bus.driver.find_element_by_class_name('experience-section')
                        try :
                            w = exp.find_element_by_css_selector('button.pv-profile-section__see-more-inline')
                            actions = ActionChains(bus.driver)
                            actions.move_to_element(w).perform()
                            bus.driver.execute_script("window.scrollTo(0, -10);")
                            time.sleep(0.5)
                            w.click()
                            time.sleep(0.5)
                        except NoSuchElementException:
                            pass
                        
                        for w in exp.find_elements_by_class_name('pv-profile-section__card-item'):
                            
                            work = w.find_element_by_class_name('pv-entity__summary-info')
                            
                            ftion ='NULL'
                            comp ='NULL'
                            date1 ='NULL'
                            date2 ='NULL'
                            loc ='NULL'
                            des = 'NULL'
        #                     print(work.get_attribute('innerHTML').encode('utf-8'))
                            try :
                                ftion = work.find_element_by_tag_name('h3').get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
        #                     print(ftion.encode('utf-8'))
                            try :
                                comp = work.find_element_by_class_name('pv-entity__secondary-title').get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
        #                     print(comp.encode('utf-8'))
        #                      date = work.find_element_by_xpath("/html/body/form[1]")
                            try :
                                date = work.find_element_by_class_name('pv-entity__date-range').find_elements_by_tag_name('span')[1].get_attribute('innerHTML')
                                try :
                                    date1 = date[0:4]
                                except:
                                    pass
                                try :
                                    date2 = date[-4:]
                                except:
                                    pass                                                        
                                print(date.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            try :                    
                                loc = work.find_element_by_class_name('pv-entity__location').find_elements_by_tag_name('span')[1].get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
                            try :                    
                                des = w.find_element_by_css_selector('p.pv-entity__description').get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
                            experience = [ftion,comp,date1,date2,loc,des]
                            experienceList.append(experience)
                            print(len(experience))
                            print(len(experienceList))
                        
                        f = open(directoryToSave+'/experience.csv', 'a')
                        
                        for e in experienceList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')).strip() + '",'
                                f.write(string)
                            f.write('\n')
                        f.close()
                        
                    except NoSuchElementException:
                        pass
                    
                    
                    
                    
                    academyList = []
                    
                    
                    try :
                        stu = bus.driver.find_element_by_class_name('education-section')
                        try :
                            stud = stu.find_element_by_css_selector('button.pv-profile-section__see-more-inline')
                            actions = ActionChains(bus.driver)
                            actions.move_to_element(stud).perform()
                            bus.driver.execute_script("window.scrollTo(0, -10);")
                            time.sleep(0.5)
                            stud.click()
                            time.sleep(0.5)
                        except NoSuchElementException:
                            pass
                        
        #                 print(stu.get_attribute('innerHTML').encode('utf-8'))
                        for s in stu.find_elements_by_class_name('pv-profile-section__card-item'):
                            stud = s.find_element_by_class_name('pv-entity__summary-info')
                            schoolname ='NULL'
                            field1 ='NULL'
                            field2 ='NULL'
                            date1 ='NULL'
                            date2 ='NULL'
                            des ='NULL'
                            print(stud.get_attribute('innerHTML').encode('utf-8'))
        #                     study = stud.find_element_by_class_name('pv-entity__degree-info')
        #                     print(study.get_attribute('innerHTML').encode('utf-8'))
                            try :
                                schoolname = stud.find_element_by_css_selector('h3.pv-entity__school-name').get_attribute('innerHTML')
                                print(schoolname.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            try :
                                field1 = stud.find_element_by_css_selector('p.pv-entity__fos').find_elements_by_tag_name('span')[1].get_attribute('innerHTML')                    
                                print(field1.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            
                            try :
                                field2 = stud.find_element_by_css_selector('p.pv-entity__grade').find_elements_by_tag_name('span')[1].get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
        
    #                         print(field2.encode('utf-8'))
                            try :
                                dates = stud.find_element_by_css_selector('p.pv-entity__dates').find_elements_by_tag_name('span')[1]
                                print(dates.get_attribute('innerHTML').encode('utf-8'))
                                try :
                                    date1 = dates.find_elements_by_tag_name('time')[0].get_attribute('innerHTML')
                                except:
                                    pass
                                try :
                                    date2 = dates.find_elements_by_tag_name('time')[1].get_attribute('innerHTML')
                                except:
                                    pass
                            except:
                                pass
                            print(date1.encode('utf-8')) 
                            print(date2.encode('utf-8'))
                            try :                    
                                des = s.find_element_by_css_selector('p.pv-entity__description').get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
                            academy = [schoolname,field1,field2,date1,date2,des]
        #                     academyEn = encode(academy)
                            academyList.append(academy)
                            
                        
                        f = open(directoryToSave+'/academy.csv', 'a')
                        
                        for e in academyList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')).strip() + '",'
                                f.write(string)
                            f.write('\n')
                        f.close()
                    except NoSuchElementException:
                        pass
                    
                    
                    
                    volunteerList = []
                    
                    
                    try :
                        v = bus.driver.find_element_by_class_name('volunteering-section')
                        try :
                            vo = v.find_element_by_css_selector('button.pv-profile-section__see-more-inline')
                            actions = ActionChains(bus.driver)
                            actions.move_to_element(vo).perform()
                            bus.driver.execute_script("window.scrollTo(0, -10);")
                            time.sleep(0.5)
                            vo.click()
                            time.sleep(0.5)
                        except NoSuchElementException:
                            pass
                        for vol in v.find_elements_by_class_name('pv-volunteering-entity'):
                            volTit ='NULL'
                            volSecTit ='NULL'
                            volDates1 ='NULL'
                            volDates2 ='NULL'
                            volLength ='NULL'
                            volDes = 'NULL'
                            print(vol.get_attribute('innerHTML').encode('utf-8'))
                            try :
                                volTit = vol.find_element_by_tag_name('h3').get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
                            print(volTit.encode('utf-8')) 
                            try :
                                volSecTit = vol.find_element_by_css_selector('span.pv-entity__secondary-title').get_attribute('innerHTML')
                                print(volSecTit.encode('utf-8')) 
                            except NoSuchElementException:
                                pass
                            try :
                                volDates = vol.find_element_by_css_selector('h4.pv-entity__date-range').find_elements_by_tag_name('span')[1].get_attribute('innerHTML')
                                try :
                                    volDates1 = volDates[0:8]
                                except:
                                    pass
                                try :
                                    volDates2 = volDates[-8:]
                                except:
                                    pass
                                
                            except:
                                pass
    #                         print(volDates.encode('utf-8')) 
                            try :
                                volLength = vol.find_element_by_css_selector('span.pv-entity__bullet-item').get_attribute('innerHTML')
                                print(volLength.encode('utf-8')) 
                            except NoSuchElementException:
                                pass
                            try :
                                volDes = vol.find_element_by_css_selector('p.pv-entity__description').get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
                            
                            volunteer = [volTit,volSecTit,volDates1,volDates2,volLength,volDes]
        #                     volunteer = encode(volunteer)
                            volunteerList.append(volunteer)
                            
                        
                        f = open(directoryToSave+'/volunteer.csv', 'a')
                        
                        for e in volunteerList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')) + '",'
                                f.write(string)
                            f.write('\n')
                        f.close()
                    except NoSuchElementException:
                        pass
                
    
                    
                    recommendationList = []
                    try :
                        recommendationSection = bus.driver.find_element_by_css_selector('section.pv-recommendations-section')
                        print(recommendationSection.get_attribute('innerHTML').encode('utf-8'))
                        try :
                            rec = recommendationSection.find_element_by_css_selector('button.pv-profile-section__see-more-inline').click()
                            actions = ActionChains(bus.driver)
                            actions.move_to_element(rec).perform()
                            bus.driver.execute_script("window.scrollTo(0, -10);")
                            time.sleep(0.5)
                            rec.click()
                            time.sleep(0.5)
                        except:
                            pass
                        
                        for recommendation in recommendationSection.find_elements_by_css_selector('li.pv-recommendation-entity'):
                            print(recommendation.get_attribute('innerHTML').encode('utf-8'))
                            recoName ='NULL'
                            recoLinkedIn ='NULL'
                            recoFunction ='NULL'
                            recoRelationship ='NULL'
                            recoComment ='NULL'
                            try :
                                recoName = recommendation.find_element_by_tag_name('h3').get_attribute('innerHTML')
                                print(recoName.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            try :
                                recoLinkedIn = recommendation.find_element_by_css_selector('a.pv-recommendation-entity__member').get_attribute('href')
                                print(recoLinkedIn.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            try :
                                recoSubSec = recommendation.find_element_by_css_selector('div.pv-recommendation-entity__detail').find_elements_by_tag_name('p')
                            except NoSuchElementException:
                                pass
                            try :
                                recoFunction = recoSubSec[0].get_attribute('innerHTML')
                                print(recoFunction.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            try :
                                recoRelationship = recoSubSec[1].get_attribute('innerHTML')
                                print(recoRelationship.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            try :
                                recoComment = recommendation.find_element_by_css_selector('blockquote.pv-recommendation-entity__text').get_attribute('innerHTML')
                                print(recoComment.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            reco = [recoName,recoLinkedIn,recoFunction,recoRelationship,recoComment]
                            recommendationList.append(reco)
                        
                        f = open(directoryToSave+'/recommandation.csv', 'a')
                        
                        for e in recommendationList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')).strip() + '",'
                                f.write(string)
                            f.write('\n')
                        f.close()
                    except NoSuchElementException:
                        pass
                    
                    booleanScroll = True
                    builder = ActionChains(bus.driver)
                    while booleanScroll:
                        try :
                            builder.move_to_element(footer).perform()
                            booleanScroll = False
                        except:
                            bus.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(0.5)
                            pass
                    
                    try :
                        element = bus.driver.find_element_by_class_name('education-section')
                        bus.driver.execute_script("arguments[0].scrollIntoView();", element)
                        
                    except NoSuchElementException:
                        try :
                            element = bus.driver.find_element_by_class_name('experience-section')
                            bus.driver.execute_script("arguments[0].scrollIntoView();", element)
                            
                        except NoSuchElementException:
                            pass
                        pass
                    
                    time.sleep(2)
                    skillList =[]   
                    try : 
                        skillSection = bus.driver.find_element_by_css_selector('section.pv-featured-skills-section')
                        print(skillSection.get_attribute('innerHTML').encode('utf-8'))
                    
                        try :
                            sect = skillSection.find_element_by_css_selector('button.pv-skills-section__additional-skills')
                            ActionChains(bus.driver).move_to_element(sect).perform()
                            bus.driver.execute_script("window.scrollTo(0, -5);")
                            sect.click()
                            time.sleep(0.5)
                        except NoSuchElementException:
                            pass
                  
                        try :
                            for skills in skillSection.find_elements_by_class_name('pv-skill-entity__skill-name'):
                                print(skills.get_attribute('innerHTML').encode('utf-8'))
                                skillTit = 'NULL'
                                try:
                                      
                                    skillTit = skills.get_attribute('innerHTML')
                                except NoSuchElementException:
                                    pass 
                                print skillTit.encode('utf-8')
                                skillList.append(skillTit)
                                  
                              
                              
                            f = open(directoryToSave+'/skills.csv', 'a')
                              
                              
                            
                            for w in skillList:
                                f.write('"' + str(lead_id) + '",')
                                string = '"' + str(w.encode('utf-8')) + '",'                        
                                f.write(string)
                                f.write('\n')
                            
                            f.close()
                          
                        except NoSuchElementException:
                            pass
                    except NoSuchElementException:
                        pass    
                    interestList = []
                     
                    try :
                        interestSection = bus.driver.find_element_by_css_selector('section.pv-interests-section')
                         
                        for interest in interestSection.find_elements_by_css_selector('li.pv-interest-entity'):
        #                     print interest.get_attribute('innerHTML').encode('utf-8')
                            interestName ='NULL'
                            interestLink ='NULL'
                            try :
                                interestName = interest.find_element_by_tag_name('span').get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
        #                     print interestName.encode('utf-8')
                            try :
                                interestLink = interest.find_element_by_css_selector('a.pv-interest-entity-link').get_attribute('href')
                            except NoSuchElementException:
                                pass
                            inter = [interestName,interestLink]
                            interestList.append(inter)
                         
                        f = open(directoryToSave+'/interest.csv', 'a')
                         
                        for e in interestList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')) + '",'
                                print string
                                f.write(string)
                            f.write('\n')
                        f.close()
                         
                        print len(interestList)
                    except NoSuchElementException:
                        pass
                    
                    try:
                        
                        moreInterestSection = bus.driver.find_element_by_css_selector('a[data-control-name="view_interest_details"]')
                        actions = ActionChains(bus.driver)
                        actions.move_to_element(moreInterestSection).perform()
                        bus.driver.execute_script("window.scrollTo(0, -10);")
                        moreInterestSection.click()
                        time.sleep(5)
                        
                        sizeList=-1
                        influencerList = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        while(len(influencerList)>sizeList):
                            
                            sizeList = len(influencerList)
                            hover = ActionChains(bus.driver).move_to_element(influencerList[-1])
                            hover.perform()
                            time.sleep(1)
                            influencerList = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        influencerSection = bus.driver.find_element_by_css_selector('a[data-control-name="following_influencers"]')
                        influencerList = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        influList = []
                        for influencer in influencerList:
                            print influencer.get_attribute('innerHTML').encode('utf-8')
                            influencerName = influencer.find_element_by_class_name('pv-entity__summary-title-text').get_attribute('innerHTML')
                            print influencerName.encode('utf-8')
                            influencerTitle = influencer.find_element_by_class_name('pv-entity__occupation').get_attribute('innerHTML')
                            influencerLink = influencer.find_element_by_class_name('pv-interest-entity-link').get_attribute('href')
                            print("TITLE")
                            print influencerTitle.encode('utf-8')
                            print("NAME    ")
                            print influencerLink.encode('utf-8')
#                             raw_input("Going with influencer")

                            influ = [influencerName,influencerTitle,influencerLink]
                            influList.append(influ)
                        
                        f = open(directoryToSave+'/influencer.csv', 'a')
                             
                        for e in influList:
                            print("YOUPI")
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                print("YES")
                                string = '"' + str(w.encode('utf-8')) + '",'
                                print string
                                f.write(string)
                            f.write('\n')
                        f.close()
                    except NoSuchElementException:
                        pass
                    
                    try:
                        companiesSection = bus.driver.find_element_by_css_selector('a[data-control-name="following_companies"]')
                        companiesSection.click()
                        
#                         hover = ActionChains(bus.driver).move_to_element(companiesList[0])
#                         hover.perform()
#                         bus.driver.find_element_by_css_selector('ul.entity-list').send_keys(Keys.END)
                        
                        time.sleep(2)
#                         bus.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scr1)
                        
                        sizeList=-1
                        companiesList = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        while(len(companiesList)>sizeList):
                            
                            sizeList = len(companiesList)
                            hover = ActionChains(bus.driver).move_to_element(companiesList[-1])
                            hover.perform()
                            time.sleep(1)
                            companiesList = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                               
                        
                        
                        time.sleep(1)
                        companiesList = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        compaList = []
                        for companies in companiesList:
                            companiesName = companies.find_element_by_class_name('pv-entity__summary-title-text').get_attribute('innerHTML')
                            companiesCount = companies.find_element_by_class_name('pv-entity__follower-count').get_attribute('innerHTML')
                            companiesLink = companies.find_element_by_class_name('pv-interest-entity-link').get_attribute('href')
                            compa = [companiesName,companiesCount,companiesLink]
                            compaList.append(compa)
                        f = open(directoryToSave+'/following_companies.csv', 'a')
                             
                        for e in compaList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')) + '",'
                                print string
                                f.write(string)
                            f.write('\n')
                        f.close()
                    except NoSuchElementException:
                        pass

                    try:
                        Section = bus.driver.find_element_by_css_selector('a[data-control-name="following_groups"]')
                        Section.click()
                        
#                         hover = ActionChains(bus.driver).move_to_element(companiesList[0])
#                         hover.perform()
#                         bus.driver.find_element_by_css_selector('ul.entity-list').send_keys(Keys.END)
                        
                        time.sleep(2)
#                         bus.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scr1)
                        
                        sizeList=-1
                        List = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        while(len(List)>sizeList):
                            
                            sizeList = len(List)
#                             scr1 = bus.driver.find_element_by_css_selector('div.entity-list-wrapper')
                            hover = ActionChains(bus.driver).move_to_element(List[-1])
                            hover.perform()
                            time.sleep(1)
                            List = bus.driver.find_elements_by_css_selector('li.entity-list-item')
#                         bus.driver.execute_script("arguments[0].scrollTop = 300", scr1)
                               
                        
                        
                        time.sleep(2)
                        List = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        bList = []
                        for item in List:
                            Name = item.find_element_by_class_name('pv-entity__summary-title-text').get_attribute('innerHTML')
                            Count = item.find_element_by_class_name('pv-entity__follower-count').get_attribute('innerHTML')
                            Link = item.find_element_by_class_name('pv-interest-entity-link').get_attribute('href')
                            basket = [Name,Count,Link]
                            bList.append(basket)
                        f = open(directoryToSave+'/following_groups.csv', 'a')
                             
                        for e in bList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')) + '",'
                                print string
                                f.write(string)
                            f.write('\n')
                        f.close()
                    except NoSuchElementException:
                        pass
                    
                    try:
                        Section = bus.driver.find_element_by_css_selector('a[data-control-name="following_schools"]')
                        Section.click()
                        
#                         hover = ActionChains(bus.driver).move_to_element(companiesList[0])
#                         hover.perform()
#                         bus.driver.find_element_by_css_selector('ul.entity-list').send_keys(Keys.END)
                        
                        time.sleep(2)
#                         bus.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scr1)
                        
                        sizeList=-1
                        List = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        while(len(List)>sizeList):
                            
                            sizeList = len(List)
#                             scr1 = bus.driver.find_element_by_css_selector('div.entity-list-wrapper')
                            hover = ActionChains(bus.driver).move_to_element(List[-1])
                            hover.perform()
                            time.sleep(1)
                            List = bus.driver.find_elements_by_css_selector('li.entity-list-item')
#                         bus.driver.execute_script("arguments[0].scrollTop = 300", scr1)
                               
                        
                        
                        time.sleep(2)
                        List = bus.driver.find_elements_by_css_selector('li.entity-list-item')
                        bList = []
                        for item in List:
                            Name = item.find_element_by_class_name('pv-entity__summary-title-text').get_attribute('innerHTML')
                            Count = item.find_element_by_class_name('pv-entity__follower-count').get_attribute('innerHTML')
                            Link = item.find_element_by_class_name('pv-interest-entity-link').get_attribute('href')
                            basket = [Name,Count,Link]
                            bList.append(basket)
                        f = open(directoryToSave+'/following_schools.csv', 'a')
                             
                        for e in bList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')) + '",'
                                print string
                                f.write(string)
                            f.write('\n')
                        f.close()
                    except NoSuchElementException:
                        pass
                    
                    try :
                        otherMember= bus.driver.find_element_by_css_selector('section.pv-browsemap-section')
                        print(otherMember.get_attribute('innerHTML').encode('utf-8'))
                        otherMemberList = []
                         
                        for member in otherMember.find_elements_by_css_selector('li.pv-browsemap-section__member-container'):
                            linkedInLink ='NULL'
                            linkedInName ='NULL'
                            linkedInDesc ='NULL'
                            print(member.get_attribute('innerHTML').encode('utf-8'))
                            try :
                                linkedInLink = member.find_element_by_css_selector('a.pv-browsemap-section__member').get_attribute('href')
                                print(linkedInLink.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            try :
                                linkedInName = member.find_element_by_tag_name('h3').find_element_by_tag_name('span').find_element_by_tag_name('span').get_attribute('innerHTML')
                                print(linkedInName.encode('utf-8'))
                            except NoSuchElementException:
                                pass
                            try :
                                linkedInDesc = member.find_element_by_css_selector('p.browsemap-headline').get_attribute('innerHTML')
                            except NoSuchElementException:
                                pass
                            
                            memberList = [linkedInLink,linkedInName,linkedInDesc]
                            otherMemberList.append(memberList)
                             
                         
                         
                        f = open(directoryToSave+'/otherMember.csv', 'a')
                         
                        for e in otherMemberList:
                            f.write('"' + str(lead_id) + '",')
                            for w in e:
                                string = '"' + str(w.encode('utf-8')) + '",'
                                f.write(string)
                            f.write('\n')    
                        f.close()
                    except NoSuchElementException:
                        pass
                    element = bus.driver.find_element_by_tag_name('body')
             
                    source_code = element.get_attribute('outerHTML')
                        
                    f = open(directoryToSave+'/full_source/' + str(lead_id) + '.html', 'w')
                    f.write(source_code.encode('utf-8'))
                    f.close()
                    f = open(directoryToSave+'/id', 'a')
                    f.write(str(lead_id)+",")
                    f.close()
                    
                    
    #                 f = open(directoryToSave+'/html_source_code.html', 'a')
    #                  
    #                 f.write(source_code.encode('utf-8'))
    #                 f.close()
#                             
            except NoSuchElementException:
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


cli.add_command(scrap)
cli.add_command(store)


if __name__ == '__main__':
    cli()
