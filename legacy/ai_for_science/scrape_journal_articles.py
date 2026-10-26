import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI
import pandas as pd
import os

os.makedirs('output',exist_ok=True)
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

openai = OpenAI()

## define website class
headers = { "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64: x64) AppleWebKit/537.36 (KHMTL, like Gecko) Chrome/117.0.0.0 Safari/537.36"}

class Website:
	def __init__(self,url):
		'''
		Create webste object from given URL using BeautifulSoup library
		'''
		self.url = url
		response = requests.get(url, headers=headers)
		soup = BeautifulSoup(response.content, 'html.parser')
		self.title = soup.title.string if soup.title else "no title found"
		for irrelevant in soup.body(["script", "style", "img", "input"]):
			irrelevant.decompose()
		self.text = soup.body.get_text(separator='\n', strip=True)

### create prompts

system_prompt = "You are an assistant that analyzes the content of scholarly articles in websites \
and provides a summary of the text, highlighting the methodology of the assessment tool: what it is and how is it used, \
ignoring text that might be navigation-related \
respond in Markdown"

def user_prompt_for(website, assessment_tool):
	user_prompt =f"You are reading an article titled {website.title}"
	user_prompt+= f"\nThe contents of the article are as follows: \
	please provide a thorough summary of the website in markdown. \
	The assessment tool is {assessment_tool}. \
	ignore all text that does not relate to the article at hand. \n\n"
	user_prompt+=website.text
	return user_prompt

### messages list
def messages_for(website, assessment_tool):
	return [
		{"role":"system", "content": system_prompt},
		{"role":"user", "content": user_prompt_for(website, assessment_tool)}
	]

### call openAI
def call_openAI(url, assessment_tool):
	sis = Website(url)
	response = openai.chat.completions.create(model='gpt-4o-mini', messages = messages_for(sis, assessment_tool))
	return response.choices[0].message.content

#### export summary
def export_summary(url, assessment_tool, title):
	article = call_openAI(url, assessment_tool)
	with open(f'output/{assessment_tool}_{title}.md', 'w') as file:
		file.write(article)


# df = pd.read_excel('bibliography.xlsx')
# # print(df.loc[0,'url'], df.loc[0,'tool'])
# for idx in df.index:
# 	export_summary(df.loc[idx,'url'], df.loc[idx,'tool'], df.loc[idx, 'title'])


export_summary('https://www.sralab.org/rehabilitation-measures/stroke-impact-scale', 'SIS', 'ShirleyRyanAbilityLab')

