import openai

# Set up your OpenAI API credentials
openai.api_key = "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"

# Define the instruction and schema
instruction = "Select button2 to go to the profile screen, then select button5 to change your profile photo."
schema = '''
    <list name='elements' description="What are the UI elements in this instruction in order? Do not include description and format, only output json output." >
        <object>
            <integer name="index" format="1-indexed" />
            <string name="UI_name" description="What is the name of this UI element?" format="one-word" on-fail-one-words="reask" />
            <integer name="UI_ID" description="What is the ID associated with this UI element? Leave blank if there's not ID" format="one-line"  />
        </object>
    </list>
'''

# Make the GPT-3 API call
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=f"schema:\n{schema}\n\ninstruction = \"{instruction}\"",
    max_tokens=256,
    n=1,
    stop=None,
    temperature=0.8
)

# Extract the JSON output from the API response
json_output = response.choices[0].text.strip()
print("JSON Output:")
print(json_output)
