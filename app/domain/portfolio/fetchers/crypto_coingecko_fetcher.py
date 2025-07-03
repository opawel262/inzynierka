import requests
import json

class CoinGeckoCryptoFetcher:
    def __init__(self, currency: str = "usd"):
        
        self.url = "https://api.coingecko.com/api/v3/coins/markets"
        self.params = {
            "vs_currency": currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "1h,24h,7d",
        }
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "CG-wS3ZzLkLQfw2xicwuWhymbR2",
        }

    def fetch_data(self):
        try:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            response.raise_for_status()  
            return response.json()
        except requests.RequestException as e:
            return None

    def save_to_file(self, data):
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"[INFO] Dane zapisane do {self.save_path}")
        except IOError as e:
            print(f"[ERROR] Błąd zapisu pliku: {e}")