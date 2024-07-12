"""
create_assistant.py
"""
import os
from openai import OpenAI

INSTRUCTIONS = """
You're world's best data scentist.

You will receive: (a) a question or task and answer the user's question or fulfill the task. 
Please answer user's question in scintific background with given files, not unspecific informations.
You will begin by carefully analyzing the question, and explain your approach in a step-by-step fashion. 
"""

# Initialise the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create a new assistant
my_assistant = client.beta.assistants.create(
    instructions=INSTRUCTIONS,
    name="Data Analyst",
    tools=[{"type": "files_attached"}],
    model="gpt-4o",
)

print(my_assistant) # Note the assistant ID
