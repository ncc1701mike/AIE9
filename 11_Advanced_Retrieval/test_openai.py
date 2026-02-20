import os
import traceback
import openai

print("Key prefix:", os.environ.get("OPENAI_API_KEY", "")[:5])

client = openai.OpenAI() # uses OPENAI_API_KEY from env

try:
    resp = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": "Say 'ping'"}],
    )
    print("Response:", resp.choices[0].message.content)
except Exception:
    traceback.print_exc()