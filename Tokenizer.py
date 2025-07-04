import tiktoken

with open('Sample Parts List - Sheet2.csv', encoding='utf-8') as f:
    text = f.read()

enc = tiktoken.encoding_for_model("gpt-4")
tokens = enc.encode(text)
print(len(tokens))