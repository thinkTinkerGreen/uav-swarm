from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()
try:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents="Say hi",
    )
    print("Success:", response.text)
except Exception as e:
    print("Error:", e)
