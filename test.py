from mexc_sdk import Spot

# Test MEXC SDK methods
client = Spot(api_key="mx0vgl7XrPqWMYq4gM", api_secret="cca301c14247424c9ad7ff4ed1351af1")
print(client.account_info())
print(client.open_orders("USD1USDT"))
