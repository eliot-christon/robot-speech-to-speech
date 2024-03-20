import requests

# Define the base URL for the server
BASE_URL = 'http://localhost:5003'

def test_start_TTS():
    response = requests.post(f'{BASE_URL}/start')
    print(response.json())

def test_get_status():
    response = requests.get(f'{BASE_URL}/status')
    print(response.json())

if __name__ == "__main__":
    # Test starting
    print("Starting TTS...")
    test_start_TTS()

    # Test getting TTS status
    print("\nGetting TTS status...")
    test_get_status()

    # Test getting TTS status
    print("\nGetting TTS status...")
    test_get_status()
