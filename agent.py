import os
import yaml

from langchain.agents import (
    create_json_agent,
    AgentExecutor
)
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.chains import LLMChain
from langchain.llms.openai import OpenAI
from langchain.requests import TextRequestsWrapper
from langchain.tools.json.tool import JsonSpec
from langchain.prompts import PromptTemplate

def init_agent():
    with open("ui.yml") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    json_spec = JsonSpec(dict_=data, max_value_length=4000)
    json_toolkit = JsonToolkit(spec=json_spec)

    json_agent_executor = create_json_agent(
        llm=OpenAI(temperature=0),
        toolkit=json_toolkit,
        verbose=True
    )


    response = json_agent_executor.run('''
        Answer queries about how to navigate through the UI by providing a list of commands setting the `highlighted` attribute of each UI element that needs to be used to answer the query to `True`. Here's an example interaction:

        Question: How do I change my username if I am on screen 1?

        Response: 
        1. Click button 1 to go to screen 2
        2. On screen 2 select the text that says username!

        Question: How do I navigate to location from screen 1?

        Response:
        ''')