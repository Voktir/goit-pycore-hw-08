import re

text = "Моя електронна адреса: example@example.com"
pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
match = re.search(pattern, text)

if match:
    print("Електронна адреса:", match.group())
    print("Valid Email")
else:
    print("Invalid Email")
