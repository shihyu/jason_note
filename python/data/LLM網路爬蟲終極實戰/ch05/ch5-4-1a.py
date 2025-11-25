str1 = "  Python is a \nprogramming language.\n\r   "

str2 = str1.replace("\n", "").replace("\r", "")
print("'" + str2 + "'")
print("'" + str2.strip() + "'")
