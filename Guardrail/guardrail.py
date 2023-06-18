import guardrails as gd

rail_str = """
<rail version="0.1">

<output>


    <list name='elemenst' description="What are the UI elements in this instruction in order?" >
        <object>
            <integer name="index" format="1-indexed" />
            <string name="UI_name" description="What is the name of this UI element?" format="one-word" on-fail-one-words="reask" />
            <integer name="UI_ID" description="What is the ID associated with this UI element?" format="one-line"  />
        </object>
    </list>

</output>


<prompt>
Given the following instruction on how to go to a page, extract the UI elements. If no elements exist in the instruction, enter 'None'.

{{instruction}}

@xml_prefix_prompt

{output_schema}

@json_suffix_prompt_v2_wo_none</prompt>

</rail>
"""

guard = gd.Guard.from_rail_string(rail_str)
print(guard.base_prompt)

import openai

instruction = "Select button1 and then you are at screen1."

raw_llm_response, validated_response = guard(
    openai.Completion.create,
    prompt_params={"instruction": instruction},
    engine='text-davinci-003',
    max_tokens=2048,
    temperature=0
)

print(f"Validated Output: {validated_response}")
