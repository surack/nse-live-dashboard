import requests
import json
from datetime import datetime

def fetch_data(symbol):
url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

```
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers)
response = session.get(url, headers=headers)

data = response.json()

records = data["records"]["data"]
spot = data["records"]["underlyingValue"]

# find ATM
atm = min(records, key=lambda x: abs(x["strikePrice"] - spot))["strikePrice"]

step = 50 if symbol == "NIFTY" else 100

strikes = [
    x for x in records
    if atm - 8*step <= x["strikePrice"] <= atm + 8*step
]

pe_oi = ce_oi = pe_coi = ce_coi = 0

for x in strikes:
    if "CE" in x and "PE" in x:
        ce_oi += x["CE"]["openInterest"]
        pe_oi += x["PE"]["openInterest"]
        ce_coi += x["CE"]["changeinOpenInterest"]
        pe_coi += x["PE"]["changeinOpenInterest"]

oi_pcr = round(pe_oi / ce_oi, 2) if ce_oi else 0
coi_pcr = round(pe_coi / ce_coi, 2) if ce_coi else 0

return {
    "time": datetime.now().strftime("%H:%M:%S"),
    "symbol": symbol,
    "oi_pcr": oi_pcr,
    "coi_pcr": coi_pcr
}
```

def main():
try:
result = fetch_data("NIFTY")

```
    with open("data.json", "r") as f:
        history = json.load(f)
except:
    history = []

history.append(result)

# keep last 50 points
history = history[-50:]

with open("data.json", "w") as f:
    json.dump(history, f)
```

if **name** == "**main**":
main()
