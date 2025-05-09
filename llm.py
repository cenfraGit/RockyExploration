from ollama import chat

stream = chat(
    model='robot_control',
    messages=[{'role': 'user', 'content': 'move forward'}],
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)
