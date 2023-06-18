from flask import Flask
from flask import render_template, jsonify, request

import json
import os
import yaml
import ast

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
            1. Select profile to change your profile

        Question: How do I go to my favorites?
        Response: 
            1. Select images to go to the images screen, then select favorites

        Question: How do I get to my profile?
        Response: 
            1. Select profile to go to the profile screen
        
        Question: How do I access my hotspot?
        Response: 
            1. Select settings to go to the settings screen, then select hotspot
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

confusion_detected = False
swift_data = 'False'

@app.route('/') # empty page
def index():
    return render_template('index.html')

@app.route('/api/confusion-detected', methods=['GET', 'POST'])
def check_confusion_detected():
    global confusion_detected

    if request.method == 'POST':
        confusion_detected = True
        return jsonify(str(True))
    else:
        return jsonify(str(confusion_detected))

@app.route('/swift', methods=['GET'])
def get_swift_data():
    '''
    reads data from json file. If json file dosen't exist then, returns the string 'data not found'
    '''
    try:
        with open('swift_data.json', 'r') as file:
            data = file.read()
            return jsonify(data)
    except FileNotFoundError:
        return 'Data not found'
    
@app.route('/api/query/<path:question>', methods=['GET', 'POST'])
def get_agent_response(question):
    # load the data
    data = load_ui_table() # load the ui_table
    
    # init the json_agent
    json_spec = JsonSpec(dict_=data, max_value_length=4000)
    json_toolkit = JsonToolkit(spec=json_spec)
    
    json_agent_executor = create_json_agent(
        llm=OpenAI(temperature=0),
        toolkit=json_toolkit,
        verbose=True # verbose false to not see CoT
    )

    # make the prompt with the question
    formatted_prompt = make_prompt(question)
    print(formatted_prompt)

    # run the prompt
    response = json_agent_executor.run(formatted_prompt)
    print(response)

    prompt = f'''
    Please analyze the response and identify the UI elements in order. 
    Return the names of these elements based on the order it was listed in response in a list format, 
    like ["element1", "element2", "element3", ...]. Do not put "Answer: " in front of the list just return a list.

    Instruction: \"{response}\"
    '''

    structured_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=256,
        n=1,
        stop=None,
        temperature=0
    ).choices[0].text.strip()

    # The model's output is a string representation of a list, 
    # so we parse it using `json.loads` to get a Python list.
    ui_elements = structured_response

    print(ui_elements)  # ["button1", "button2", "button3", ...]

    swift_data = dict({})
    swift_data['voice'] = response
    swift_data['ui_elements'] = ast.literal_eval(ui_elements)

    # write to swift dict
    with open("swift_data.json", "w") as outfile:
        json.dump(swift_data, outfile)
    
    return jsonify(ui_elements)
