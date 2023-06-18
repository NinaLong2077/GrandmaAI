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
    with open("ui.yml") as f:
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
        1. Select profile to go to the profile screen, then select username

    Question: How do I change my profile?
    Response: 
        1. Select profile to go to the profile screen

    Question: How do I get to my profile?
    Response: 
        1. Select profile to go to the profile screen
    
    Question: How do I get to search?
    Response: 
        1. Select profile to go to the profile screen, then select profile_button1 to get to the search screen
    

        =============================
        Given the above context, answer the user's question.
        
        Question: {question} assuming that the user is currently on the home screen?

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

@app.route('/api/<path:question>', methods=['GET', 'POST'])
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

    response = "Select button2 to go to the profile screen, then select button5 to change your profile photo."

    prompt = f'''
    Please analyze the response and identify the UI elements in order. Return the names of these elements based on the order it was listed in response in a list format, like ["element1", "element2", "element3", ...]. 
    If the UI element is like "button 2", make it "button2" in the list.

    Instruction: \"{response}\"
    '''

    structured_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=256,
        n=1,
        stop=None,
        temperature=0.8
    ).choices[0].text.strip()

    # The model's output is a string representation of a list, 
    # so we parse it using `json.loads` to get a Python list.
    ui_elements = structured_response

    print(ui_elements)  # ["button1", "button2", "button3", ...]

    return jsonify(ui_elements)
