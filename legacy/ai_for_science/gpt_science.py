import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display
from openai import OpenAI

import io
import PyPDF2
import os

os.makedirs('output/',exist_ok=True)
os.makedirs('output/sex_differences/',exist_ok=True)

h1 = 'Here are some papers I found to be quite helpful for understanding how to apply the negative binomial model in epidemiology. I am investigating how the infant age, maternal smoking, gestational term or preterm, and baby sex influence the death count of Sudden Unexpected Infant Death in the USA; We conducted a population-based incidence study to evaluate risk factors for SUID using Negative Binomial Regression with a population offset. Please identify whether the reference manuscript methodology align with my approach.'
# h1 = 'Here is the documentation of the PRAMS dataset. The underlying research question seeks to investigate whether family paid leave has an affect on the rate of Sudden Unexpected Infant Death. The objective is to identify which variables are potentially affected by paid leave.'

########### housekeeping 
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if api_key and api_key.startswith('sk-proj-') and len(api_key)>10:
    print("API key looks good so far")
else:
    print("There might be a problem with your API key? Please visit the troubleshooting notebook!")
    
openai = OpenAI()

### first
# A class to represent a Webpage

# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

## first create an object from class website
class Website:
    """
    A utility class to represent a Website that we have scraped, now with links
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content

        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"



        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

## next a class to create a PDF document
class Document:
    """
    A utility class to represent a Website that we have scraped, now with links
    supports both local files and URLs
    """

    def __init__(self, source, is_url=True):
        '''
        Initialize a Document object from either url or a local file path

        Args:
            source(str) URL or file path to the PDF
            is_url boolean flag indicating if source is a URL (True) or a local file path (False)

        '''
        self.source =source
        self.is_url = is_url

        if is_url:
            # handle url source
            self.url= source
            response = requests.get(source)
            self.body = response.content

        else: 
            # handle local files
            self.url = None
            with open(source,'rb') as file:
                self.body = file.read()

        pdf_file = io.BytesIO(self.body)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        self.title = source[18:-3]
        # if pdf_reader.metadata and '/Title' in pdf_reader.metadata:
        #     self.title = pdf_reader.metadata['/Title']
        # else:
        #     self.title = f'PDF from {self.url}'
        text_parts=[]
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_parts.append(page.extract_text())
        
        self.text = '\n\n'.join(text_parts)
        self.links=[]

    def get_contents(self):
        source_type='URL' if self.is_url else 'File'
        return f"Document Title:\n{self.title}\nSource :\n{self.source}\nContents:\n{self.text}\n\n"


def process_pdf_directory(directory_path:str)-> List[Document]:
    '''
    Find all PDF files in a directory and process them into document objects
    Args:
        directory_path(str): path to directory containing PDF files
    returns:
        list[Document]: list of document objects created from PDFs

    '''
    documents=[]
    for root,_,files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root,file)
                try:
                    # create a document object for each pdf file
                    print(file_path)
                    doc = Document(file_path, is_url=False)
                    documents.append(doc)
                    # print(f'Processed: {file_path}\n\n{file_path[18:]}\n')
                except Exception as e:
                    print(f'Error Processing {file_path}: {e}')
    return documents


# combined
def get_vars(url):
    doc = Document(url)
    response = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages =[
        {"role":"system", "content": vars_system_prompt},
        {"role":"user", "content": get_links_user_prompt(doc)}
        ],
        response_format = {'type':'json_object'}
        )
    result = response.choices[0].message.content
    return json.loads(result)


################# scrape relevant journals and publications to better train the model

#################
# v1 = get_vars("https://data.nber.org/nvss/linkco/orig/LinkCO15Guide.pdf")

# system_prompt = "You are an assistant that analyzes the contents of several scholarly manuscript documents.\
# The research question is understanding how paid family serves a protecting effect for Sudden Infant Unexpected Death; for example, it may facilitate breastfeeding. Your job is to understand the documents and thoroughly explain and summarize the results and methods.\
# Write a thorough summary (700 words) of each scholarly article, have both a laymen explanation and a scientific explanation; summarize and each each article in the context of the research question.\
# Respond in markdown."
system_prompt = "You are an assistant that analyzes the contents of several scholarly manuscript documents.\
The goal is to educate an epidemiologist who's reviewing my manuscript and giving me a hard time because he's not familiar with the Negative Binomial Model. Your goal is to systematically explain that the NB model is widely used and has already been used in specific and useful/informative circumstances.\
Write a thorough summary (700 words) of each scholarly article, have both a laymen explanation and a scientific explanation; summarize and each each article in the context of the research goal.\
Respond in markdown."

def get_user_prompt(hypothesis, doc):
    user_prompt = f"You are investigating the working hypothesis: {h1}"
    user_prompt+= f"Here are the scholarly manuscripts for your analyses.\n"
    # user_prompt+= str(get_vars(url))
    user_prompt+= doc.text
    return user_prompt

def design_research(hypothesis, doc,trial):
    response = openai.chat.completions.create(
        model = 'gpt-4o-mini',
        messages =[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": get_user_prompt(hypothesis, doc)}
        ])
    result = response.choices[0].message.content

    # with open(f'output/summary_{doc.title}.md', 'w', encoding='utf-8') as file:
    # with open(f'paid_leave/summary_{doc.title}.md', 'w', encoding='utf-8') as file:
    with open(f'output/sex_differences/summary_{doc.title}.md', 'w', encoding='utf-8') as file:
        file.write(result)




pdf_docs = process_pdf_directory('epidemiology_NB')


for x in range(0,len(pdf_docs)):
    dox = pdf_docs[x]
    design_research(h1, dox,x)