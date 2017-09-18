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
import re


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


def splitFileRandomly(batchSize,filename):
    directoryFile = os.path.dirname(filename)
    basefilename = os.path.basename(filename)
    
    with open(filename) as f:
        lines = f.readlines()
        lines = lines[1:]
        
    directory = "listEmailsTreated/externalData/"+ basefilename + "/" + str(batchSize)
    if not os.path.exists(directory):
        os.makedirs(directory)
                
    f = open(directory+ '/emails0.csv', 'w') 
    f.write('Email Address')
    f.write('\n')          
    p = 0;
    fileNumber = 1
                
    for email in lines:
            email = email.strip()
            email = string.replace(email, '"', '')
            email = str(email)
            

            addressToVerify =email
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)
            
            if match != None:
                if(len(email)>5):
                    f.write(email)
                    f.write('\n')
                    p +=1
            if(p==batchSize):
                p=0
                f.close()
                f = open(directory+ '/emails'+ str(fileNumber) +'.csv', 'w')
                f.write('Email Address')
                f.write('\n')      
                fileNumber += 1
#             else:
#                 if(fileNumber==4):
#                     exit
def crawl():
    batchSize = 2600
    
    
#     filename = 'ExternalData/emails_only/35k Leads Full MT4.csv'
    filename = 'Dan/list_Dan_email_only.csv'
    directoryFile = os.path.dirname(filename)
    basefilename = os.path.basename(filename)
    
    with open(filename) as f:
        lines = f.readlines()
        lines = lines[1:]
        
#     directory = "listEmailsTreated/externalData/"+ basefilename + "/" + str(batchSize)
    directory = "Dan/" + str(batchSize)
    if not os.path.exists(directory):
        os.makedirs(directory)
                
    f = open(directory+ '/emails0.csv', 'w') 
    f.write('Email Address')
    f.write('\n')          
    p = 0;
    fileNumber = 1
                
    for email in lines:
            email = email.strip()
            email = string.replace(email, '"', '')
            email = str(email)
            

            addressToVerify =email
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)
            
            if match != None:
                if(len(email)>5):
                    f.write(email)
                    f.write('\n')
                    p +=1
            else:
                print(email)
                pass
            if(p==batchSize):
                p=0
                f.close()
                f = open(directory+ '/emails'+ str(fileNumber) +'.csv', 'w')
                f.write('Email Address')
                f.write('\n')      
                fileNumber += 1
#             else:
#                 if(fileNumber==4):
#                     exit

            
                
if __name__ == '__main__':
    crawl()
