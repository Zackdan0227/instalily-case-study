import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def test_google_cse():
    """
    Test if Google Custom Search API is working.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("❌ Missing GOOGLE_API_KEY or GOOGLE_CSE_ID in environment.")
        return

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": "GE WR55X10942 site:partselect.com",
        "num": 3
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "items" in data:
        print("\n✅ API is working! Here are some results:")
        for item in data["items"]:
            print(f"🔹 {item['title']}\n   {item['link']}\n")
    else:
        print("\n❌ API is not returning results.")
        print("Full Response:", data)

if __name__ == "__main__":
    test_google_cse()
