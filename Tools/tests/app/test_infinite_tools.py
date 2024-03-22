import requests
import time

# Define the base URL for the server
BASE_URL = 'http://localhost:5007'

def test_start():
    response = requests.post(f'{BASE_URL}/start')
    print(response.json())

def test_stop():
    response = requests.post(f'{BASE_URL}/stop')
    print(response.json())

def test_get_status():
    response = requests.get(f'{BASE_URL}/status')
    print(response.json())

if __name__ == "__main__":
    # Test starting
    print("Starting...")
    test_start()

    # Wait for a while to simulate some time
    time.sleep(16)

    # Test stopping
    print("\nStopping...")
    test_stop()

    # Test getting status
    print("\nGetting status...")
    test_get_status()
