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
###### working hypothesis
# h1 = 'There are sex differences in Sudden Infant Death Syndrome.'
h1 = 'More males than females due due to Sudden Infant Death Syndrome. But is this because more total males are born or is it because of a male predisposition?'

# Initialize and constants

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if api_key and api_key.startswith('sk-proj-') and len(api_key)>10:
    print("API key looks good so far")
else:
    print("There might be a problem with your API key? Please visit the troubleshooting notebook!")
    
openai = OpenAI()

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

class Document:
    """
    A utility class to represent a Website that we have scraped, now with links
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content

        pdf_file = io.BytesIO(self.body)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        if pdf_reader.metadata and '/Title' in pdf_reader.metadata:
            self.title = pdf_reader.metadata['/Title']
        else:
            self.title = f'PDF from {self.url}'
        text_parts=[]
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_parts.append(page.extract_text())
        
        self.text = '\n\n'.join(text_parts)
        self.links=[]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

# get an object for a website
# doc = Document("https://data.nber.org/nvss/linkco/orig/LinkCO15Guide.pdf")

## system prompt for stating initial conditions
vars_system_prompt = f"You are a provided with a list of variables found on a research document.\
You are able to decide which of the variables would be most relevant to include in a research study about a given hypothesis,\
The hypothesis is: {h1}"
vars_system_prompt += "You should respond in JSON as in this example:"
vars_system_prompt += """
{
    "variables": [
        {"short": "DOB_TT", "full": "time of birth"},
        {"short": "MAGER9": "full": "Mother's Age recode 9"}
    ]
}
"""


## user prompt
def get_links_user_prompt(doc):
    user_prompt = f"Here are the contents of the research document.\n"
    user_prompt += "Please decide which of these are relevant variables for the research study and working hypothesis, respond in JSON format. \
    \n"
    user_prompt += "Full text (it is you job to read and identify variables):\n"
    user_prompt += "\n".join(doc.text)
    user_prompt = user_prompt[:100000]
    return user_prompt


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

system_prompt = "You are ab assistant that analyzes the contents of several research documents from a database documentation.\
You have a list of variables from the document that have been considered relevant to the hypothesis.\
You have the working hypothesis, list of variables, and research questions; your job is to formulate a research design including all of them!\
Include the rationale for the research question, whether it has been studied or reported in the past.\
After formulating the research question and variables that will be tested, also recommend a statistical test to assess differences, and speculate how to interpret the statistical test results.\
Respond in markdown."

def get_user_prompt(hypothesis, url):
    user_prompt = f"You are investigating the working hypothesis: {hypothesis}"
    user_prompt+= f"Here are variables of interest; use this information to formulate three research questions to test the working hypothesis. Respond in markdown.\n"
    user_prompt+= f"Variables:\n"
    user_prompt+= str(get_vars(url))
    return user_prompt

def design_research(hypothesis, url,trial):
    response = openai.chat.completions.create(
        model = 'gpt-4o-mini',
        messages =[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": get_user_prompt(hypothesis, url)}
        ])
    result = response.choices[0].message.content

    with open(f'output/hypothesis_{trial}.md', 'w', encoding='utf-8') as file:
        file.write(result)



design_research(h1, "https://data.nber.org/nvss/linkco/orig/LinkCO15Guide.pdf",4)
















