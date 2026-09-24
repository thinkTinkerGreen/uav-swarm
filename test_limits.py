from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

for model in ['gemini-3.5-flash', 'gemini-3.6-flash', 'gemini-3.7-flash', 'gemini-3.8-flash', 'gemma-4-26b-a4b-it']:
    try:
        response = client.models.generate_content(
            model=model,
            contents="say hi",
        )
        print(f"Success for {model}: {response.text}")
    except Exception as e:
        print(f"Error for {model}: {e}")
