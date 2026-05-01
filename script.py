import requests
import json
from datetime import datetime

def fetch_data(symbol):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    session.get("https://www.nseindia.com", headers=headers)

    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    response = session.get(url, headers=headers)

    data = response.json()

    records = data["records"]["data"]
    spot = data["records"]["underlyingValue"]

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
        new_data = fetch_data("NIFTY")

        try:
            with open("data.json") as f:
                history = json.load(f)
        except:
            history = []

        history.append(new_data)
        history = history[-50:]

        with open("data.json", "w") as f:
            json.dump(history, f)

    except Exception as e:
        print("ERROR:", str(e))


if __name__ == "__main__":
    main()
