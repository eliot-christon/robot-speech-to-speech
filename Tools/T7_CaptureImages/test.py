import requests
import time

# Define the base URL for the server
BASE_URL = 'http://localhost:5007'

def test_start_capturing():
    response = requests.post(f'{BASE_URL}/start')
    print(response.json())

def test_stop_capturing():
    response = requests.post(f'{BASE_URL}/stop')
    print(response.json())

def test_get_capturing_status():
    response = requests.get(f'{BASE_URL}/status')
    print(response.json())

if __name__ == "__main__":
    # Test starting capturing
    print("Starting capturing...")
    test_start_capturing()

    # Wait for a while to simulate some capturing time
    time.sleep(16)

    # Test stopping capturing
    print("\nStopping capturing...")
    test_stop_capturing()

    # Test getting capturing status
    print("\nGetting capturing status...")
    test_get_capturing_status()
