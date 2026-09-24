import re

with open("agent.py", "r") as f:
    content = f.read()

retry_logic = """
            if self.backend == "gemini":
                model_name = 'gemma-4-26b-a4b-it'
                for attempt in range(10):
                    try:
                        response = self.client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        text = response.text
                        break
                    except Exception as ex:
                        if '404' in str(ex) or 'not found' in str(ex).lower():
                            print(f"{model_name} not found. Falling back...")
                            model_name = 'gemini-3.6-flash'
                            continue
                        elif '429' in str(ex) or 'quota' in str(ex).lower():
                            print(f"Rate limited on {model_name}. Sleeping 15 seconds...")
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
