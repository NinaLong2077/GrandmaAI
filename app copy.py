from flask import Flask
from flask import render_template, make_response, jsonify

import json
import os
import yaml

from langchain.agents import (
    create_json_agent,
    AgentExecutor
)
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.llms.openai import OpenAI
from langchain.tools.json.tool import JsonSpec
from langchain.prompts import PromptTemplate
import openai
from dotenv import load_dotenv

load_dotenv() # load env variables

def load_ui_table():
    with open("ui_2.yml") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

def make_prompt(question):
    template = '''
        You are a helpful agent that answers queries about how to navigate through the UI given UI information
        by providing a list of actions to do (e.g. Click button X to go to screen Y)
        
        Here's an example interaction:
        
        ============EXAMPLE INTERACTION============
    Question: How do I change my username?
    Response: 
        1. Select button2 to go to the profile screen, then select username

    Question: How do I change my profile?
    Response: 
        1. Select button2 to go to the profile screen

        =============================
        Given the above context, assuming that the user is currently on screen 1, answer the user's question.
        
        Question: {question}?

        Response:
        '''
    prompt = PromptTemplate.from_template(template)
    formatted_prompt = prompt.format(question=question)
    return formatted_prompt

# init flask app
app = Flask(__name__)

@app.route('/') # empty page
def index():
    return render_template('index.html')

@app.route('/api/<path:question>')
def get_agent_response(question):
    # load the data
    data = load_ui_table() # load the ui_table
    
    # init the json_agent
    json_spec = JsonSpec(dict_=data, max_value_length=4000)
    json_toolkit = JsonToolkit(spec=json_spec)
    
    json_agent_executor = create_json_agent(
        llm=OpenAI(temperature=0),
        toolkit=json_toolkit,
        verbose=True # verbose false so we don't see CoT
    )

    # make the prompt with the question
    formatted_prompt = make_prompt(question)
    print(formatted_prompt)

    # run the prompt
    response = json_agent_executor.run(formatted_prompt)
    print(response)

    # Define the instruction and schema
    schema = '''
        <list name='elements' description="What are the UI elements in this instruction in order? Do not include description and format, only output json output. If it is button 2, UI_name="button2" >
            <object>
                <integer name="index" format="1-indexed" />
                <string name="UI_name" description="What is the name of this UI element?" format="one-word" on-fail-one-words="reask" />
                <integer name="UI_ID" description="What is the ID associated with this UI element? Leave blank if there's not ID" format="one-line"  />
            </object>
        </list>
    '''

    structured_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"schema:\n{schema}\n\ninstruction = \"{response}\"",
        max_tokens=256,
        n=1,
        stop=None,
        temperature=0.8
    )
    
    # Extract the JSON output from the API response
    json_output = structured_response.choices[0].text.strip()
    print("JSON Output:")
    print(json_output)

    final_response = {}
    final_response['voice'] = response
    final_response['ui_elements'] = json_output

    return final_response
