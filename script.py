import requests
import json
from datetime import datetime

def fetch_data(symbol):
    print("Fetching data...")

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json"
    }

    # Step 1: get cookies
    session.get("https://www.nseindia.com", headers=headers)

    # Step 2: fetch option chain (with fallback proxy)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    response = session.get(url, headers=headers)

    print("Status code:", response.status_code)

    # fallback if blocked
    if response.status_code != 200:
        print("Trying proxy fallback...")
        proxy_url = f"https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        response = requests.get(proxy_url)

    if response.status_code != 200:
        raise Exception("Failed to fetch NSE data")

    data = response.json()

    records = data["records"]["data"]
    spot = data["records"]["underlyingValue"]

    print("Spot:", spot)

    # find ATM
    atm = min(records, key=lambda x: abs(x["strikePrice"] - spot))["strikePrice"]

    step = 50 if symbol == "NIFTY" else 100

    strikes = [
        x for x in records
        if atm - 8*step <= x["strikePrice"] <= atm + 8*step
    ]

    pe_oi = ce_oi = pe_coi = ce_coi = 0

    for x in strikes:
        if x.get("CE") and x.get("PE"):
            ce_oi += x["CE"]["openInterest"]
            pe_oi += x["PE"]["openInterest"]
            ce_coi += x["CE"]["changeinOpenInterest"]
            pe_coi += x["PE"]["changeinOpenInterest"]

    oi_pcr = round(pe_oi / ce_oi, 2) if ce_oi else 0
    coi_pcr = round(pe_coi / ce_coi, 2) if ce_coi else 0

    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "oi_pcr": oi_pcr,
        "coi_pcr": coi_pcr
    }


def main():
    try:
        result = fetch_data("NIFTY")

        print("PCR:", result)

        try:
            with open("data.json") as f:
                history = json.load(f)
        except:
            history = []

        history.append(result)
        history = history[-50:]

        with open("data.json", "w") as f:
            json.dump(history, f)

        print("Data saved successfully")

    except Exception as e:
        print("ERROR:", str(e))


if __name__ == "__main__":
    main()
