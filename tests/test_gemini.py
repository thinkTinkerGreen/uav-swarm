import os
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env"))

from google import genai
client = genai.Client()

prompt = "Hello"
try:
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
    )
    print("SUCCESS:", response.text)
except Exception as e:
    print("ERROR:", e)
