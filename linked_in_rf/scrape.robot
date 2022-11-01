*** Settings ***
Documentation  Scrapey
Library  OperatingSystem
Library  SeleniumLibrary
Library  ${CURDIR}/rf_functions.py
Library  ${CURDIR}/CustomSeleniumLibrary.py
Variables  ${CURDIR}/variables.py
Suite Teardown  close all browsers
*** Variables ***
${BROWSER}  Chrome
${cookiefilename}  ${CURDIR}/cookies.pkl

*** Tasks ***
#This is test case one
Ready browser
    Create Webdriver  ${BROWSER}  executable_path=${CURDIR}/chromedriver.exe
    ${webdriver}=  CustomSeleniumLibrary.Get Webdriver Instance
#    Go to Homepage, log in and Load/Save cookies
    Go To  ${LOGIN}
    rf_functions.Cookies Set  ${webdriver}  ${cookiefilename}
    Go To  ${LOGIN}
    ${location}=  Get Location
    IF  "${location}" != "https://www.linkedin.com/feed/"
        Login
        Log  'Saving cookies'
        rf_functions.Cookies Get  ${webdriver}   ${cookiefilename}
    ELSE
        Log  Get Location
    END

#    IF page should contain textfield  id:app__container  Sign in
#
#    ${dbuser}=  rf_database_operations.Get User Info  ${USERNAME}
#    Should Be Equal  ${dbuser}[firstname]  ${FIRSTNAME}
#    Should Be Equal  ${dbuser}[lastname]  ${LASTNAME}
#    Should Be Equal  ${dbuser}[phone]  ${PHONE}


*** Keywords ***
Go to Homepage, log in and Load/Save cookies
    [Documentation]  Log in and leave the site authenticated
    rf_functions.Cookies Set  ${driver}
    Go To  ${LOGIN}

Login
    Input Text  id:username  ${USERNAME}
    Input Text  id:password  ${PASSWORD}
    Press Keys  id:password  ENTER



