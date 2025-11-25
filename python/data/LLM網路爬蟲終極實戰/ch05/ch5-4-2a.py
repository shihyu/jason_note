import re

phone = "0938-111-456 # Phone Number"

num = re.sub(r"#.*$", "", phone)
print(num)
num = re.sub(r"\D", "", phone)
print(num)
