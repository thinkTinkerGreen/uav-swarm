import re

with open("agent.py", "r") as f:
    content = f.read()

# We will add a simple retry loop around the Gemini API call
retry_logic = """
            if self.backend == "gemini":
                for attempt in range(10):
                    try:
                        response = self.client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=prompt,
                        )
                        text = response.text
                        break
                    except Exception as ex:
                        if '429' in str(ex) or 'quota' in str(ex).lower():
                            print("Rate limited. Sleeping 15 seconds...")
                            import time
                            time.sleep(15)
                        else:
                            raise ex
                else:
                    raise Exception("Max retries exceeded")
"""

content = re.sub(r'            if self.backend == "gemini":\n.*?(?=\n            elif self.backend == "ollama":)', retry_logic.strip('\n'), content, flags=re.DOTALL)

with open("agent.py", "w") as f:
    f.write(content)
