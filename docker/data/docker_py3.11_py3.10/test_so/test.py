import test

bitopro_client = test.login()
response = bitopro_client.get_currencies()
print("List of currencies: ", response)
