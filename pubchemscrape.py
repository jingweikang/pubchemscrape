##### Python script to automate webscraping chemical information ######
##### Written for: Chec Consulting, Everycs Project, Spring 2018 ######
#####                   Author: Jingwei Kang                     ######

from bs4 import BeautifulSoup
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import csv

##### 1. Methods for scraping CAS number and finding URL #####

# Get CAS number for a chemical from NIST.gov
# param: chemical should be a string
def get_CAS_NIST(chemical):
    url = get_NIST_URL(chemical)

    try:
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        CAS = html_soup.find_all('ul')[4].find_all('li')[6]
        return CAS.get_text().split(': ')[1]
    except:
        return None # or np.nan?

# Get CAS number for a chemical from Wikipedia
# param: chemical should be a string
def get_CAS_wiki(chemical):
    url = get_wiki_URL(chemical)
    try:
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')

        # Due to Wikipedia natural-language processing, we need to verify
        # that the title of the page is the same as the search entry.
        page_title = html_soup.find_all('h1', id = 'firstHeading')[0].get_text()
        if (chemical.lower() == page_title.lower()):
            return html_soup.find_all('span', attrs={'title': 'www.commonchemistry.org'})[0].get_text()
        else:
            return None
    except:
        return None

# Uses both NIST and Wikipedia for optimal output
# param: chemical should be a string
def get_CAS(chemical):
    x = get_CAS_wiki(chemical)
    if x == None:
        x = get_CAS_NIST(chemical)
    return x

# Get NIST url given chemical name, since html is easy to scrape
# param: chemical should be a string
def get_NIST_URL(chemical):
    url_start = 'https://webbook.nist.gov/cgi/cbook.cgi?Name='
    url_end = '&Units=SI'
    return url_start + chemical + url_end

# Get PubChem url given CAS number (if a CAS number exists
# we can be sure the url is correct)
# param: chemical should be a string
def get_PubChem_URL(chemical):
    # CAS numbers here should retain the "-", or it will be confused with CID.
    url_start = 'https://pubchem.ncbi.nlm.nih.gov/compound/'
    return url_start + chemical

# Get Wikipedia url given chemical name, since html is easy to scrape
# param: chemical should be a string
def get_wiki_URL(chemical):
    url_start = 'https://en.wikipedia.org/wiki/'
    return url_start + chemical

##### 2. Methods to find uses on PubChem #####

# Scrape for chemical uses using Selenium and PhantomJS to navigate JavaScript
# param: PubChem url of chemical
def get_uses(url):
    try:
        driver.get(url)

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Uses")))
        try:
            uses = driver.find_element_by_id('Uses')
            uses = uses.text
            print('    Found uses.')
        except NoSuchElementException as e:
            print('    Could not find uses.')
            uses = ''
    except TimeoutException as te:
        uses = ''
        print('    Failed to establish connection')
    return uses

# Cleans the string retrieved from PubChem
# param: uses should be a string input
def clean_uses(uses):
    lines = uses.replace('->', ', ').split('\n')
    # TODO: replace ", for" with " "
    # Remove entries unlikely to be uses
    cleaned = [line for line in lines if is_use(line)]
    return ', '.join(cleaned)

# Remove strings where each word is capitalized (usually a title) or start with from (indicating a source)
# param: string
def is_use(str):
    if not str:
        return False
    words = str.split(' ')
    if words[0] == 'from':
        return False
    for word in words:
        if word[0].islower():
            return True
    return False

##### 3. Methods for writing to and modifying excel files to specifications #####

# Write the CAS number and PubChem url of chemicals into a CSV file
# param: input CSV filename as a string
# param: output CSV filename as a string
def write_excel(input_file, output_file):
    with open(input_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        with open(output_file, 'w') as new_file:
            csv_writer = csv.writer(new_file)

            csv_writer.writerow(next(csv_reader)) # write the heading

            for row in csv_reader:
                chemical_name = row[0]
                print('Scraping for: ' + chemical_name)
                chemical_CAS = get_CAS(chemical_name)
                if chemical_CAS is not None and is_CAS_number(chemical_CAS):
                    newline = [chemical_name, chemical_CAS, get_PubChem_URL(chemical_CAS)]
                    csv_writer.writerow(newline)
                    print('    Successful scrape for: CAS ' + chemical_CAS)
                else:
                    csv_writer.writerow([chemical_name, None, None])
                    print('    Unsuccessful scrape for: ' + chemical_name)

# Determine if input string is a correct CAS number
# param: CAS as a string
def is_CAS_number(CAS):
    if CAS is None:
        return False
    else:
        try:
            x = float(str(CAS).replace('-', ''))
            return True
        except:
            return False

# Visits PubChem to determine the uses of each chemicals
# param: input CSV filename as a string
# param: output CSV filename as a string
def write_uses(input_file, output_file):
    with open(input_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        with open(output_file, 'w') as new_file:
            csv_writer = csv.writer(new_file)

            csv_writer.writerow(next(csv_reader)) # write the heading

            for row in csv_reader:
                chemical = row[0]
                CAS = row[1]
                url = row[2]
                print('Finding uses for: ' + chemical)
                if url:
                    uses = get_uses(url)
                    # Wasn't working on first try so loop
                    # for i in range(5):
                    #     print('  Try: ' + str(i + 1) + ', wait one second')
                    #     uses = get_uses(url)
                    #     driver.implicitly_wait(1)
                    #     if uses:
                    #         break
                    cleaned_uses = clean_uses(uses)
                    newline = [chemical, CAS, url, cleaned_uses]
                    csv_writer.writerow(newline)
                else:
                    print('    No URL provided.')
                    newline = [chemical, CAS, url, '']
                    csv_writer.writerow(newline)

# Takes the uses of each chemical and creates a new row for each use
# param: input CSV filename as a string
# param: output CSV filename as a string
def make_rows_for_uses(input_file, output_file):
    with open(input_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        with open(output_file, 'w') as new_file:
            csv_writer = csv.writer(new_file)

            csv_writer.writerow(next(csv_reader)) # write the heading

            for row in csv_reader:
                chemical = row[0]
                CAS = row[1]
                url = row[2]
                uses = row[3]
                print("Making rows for: " + chemical)
                if uses:
                    for use in split_uses(uses):
                        newline = [chemical, CAS, url, use]
                        csv_writer.writerow(newline)
                else:
                    newline = [chemical, CAS, url, '']
                    csv_writer.writerow(newline)

# Split a sentence of uses into a list of individual uses.
# param: uses as a string
def split_uses(uses):
    # Treat periods, "and", commas, colons, etc. as delimiters for uses
    split_use = uses.replace(', for', 'for')
    split_use = split_use.replace('. ', ', ')
    split_use = split_use.replace(', and ', ', ')
    split_use = split_use.replace('; ' , ', ')
    split_use = split_use.replace('However, ' , ', ')
    split_use = split_use.replace(', not otherwise listed', ', ')
    split_use = split_use.replace(', which', 'which')
    # Split the string by delimiters
    split_use = split_use.split(', ')
    return [use for use in split_use if use]

# Open driver
driver = webdriver.PhantomJS()

# Start from raw chemical names.
# write_excel('sample_chemicals1.csv', 'sample_output1.csv')

# Utilize urls to find uses
write_uses('sample_output1.csv', 'sample_output2.csv')

# Reformat entries with uses.
# make_rows_for_uses('sample_output2.csv', 'sample_output3.csv')

# Close driver
driver.quit()
