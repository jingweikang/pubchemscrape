# pubchemscrape
Python script to scrape PubChem for chemical uses.

Made by Jingwei Kang 2018.

## Motivation
This script was written for a consulting project to automate the searching of chemical CAS numbers and uses on PubChem.
Although PubChem is fairly well-structured, parsing the JavaScript with PhantomJS and Selenium is slow and guessing the
URL based on the inputs given to us was somewhat unreliable. Instead, BeautifulSoup is initially used to quickly scrape
the HTML code of sites such as NIST (very quick) and Wikipedia (which was a surprisingly useful source thanks to the natural-
language processing used in searching). This initial scrape quickly gathers the CAS numbers for the given chemicals and
then accurately generates the PubChem URLs with this identification number. Finally, the PubChem sites are scraped for
the chemical uses, which are then exported as a csv file with one use per row.

## Prerequisites
1. Obtain a list of chemicals and place them in a starter file with column headings for chemical name, CAS number,
PubChem URL, and uses.
2. Create 3 intermediate output csv files. The script first gathers the CAS numbers to accurately determine URLs before
actually visiting the PubChem sites; these outputs allow users to troubleshoot and optimize each step of the process.

## Usage
Run the provided script, making sure to change the name of input and output files in the last couple of rows.

sample_chemicals.csv provides the formatting of the first input file.
sample_output1.csv is created after reading in the chemical file and filling in the CAS numbers and PubChem URLs.
sample_output2.csv is the result of extracting the chemical uses from PubChem, with some cleaning done on the output.
sample_output3.csv is the result of splitting each use of a chemical into an individual row based on certain delimiters.

## Areas of Improvement
Several optimizations can be performed to improve the final yield of uses. Based on the inputs provided (obtained from
a regulations list online), the script can find the CAS numbers and thus the URLs of ~50% of the chemicals. Of the chemicals with
CAS numbers, the script is able to extract uses for roughly ~30%. This translates to complete success for only ~15% of inputs.
This can be inproved by:
1. Applying some sort of natural-language processing and massaging the input chemical names so that they return more results
when searched in Wikipedia.
2. Potentially waiting longer before determining a TimeoutError in Selenium or searching for more tag IDs than just "Uses". However,
both of these options come with a time tradeoff.

Finally, more testing of common sentence structure is needed to more accurately filter irrelevant results from the PubChem uses and to
avoid splitting two similar uses into two separate rows.  
