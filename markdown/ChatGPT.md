# DEMO
```
import os

from openai import OpenAI

os.environ['no_proxy'] = '*'

client = OpenAI(api_key="your_private_openai_key")

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "Do you know String Theory?",
        },
    ],
)
print(completion.choices[0].message.content)
```
