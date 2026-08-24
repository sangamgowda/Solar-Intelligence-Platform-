import requests

def test_analytics():
    try:
        response = requests.get("http://localhost:8000/analytics/model-performance")
        if response.status_code == 200:
            data = response.json()
            print("Summary LSTM:", data['summary']['lstm'])
            print("Summary LGBM:", data['summary']['lgbm'])
            print("Table Data Length:", len(data['table_data']))
            if data['table_data']:
                print("Last Item:", data['table_data'][-1])
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_analytics()
