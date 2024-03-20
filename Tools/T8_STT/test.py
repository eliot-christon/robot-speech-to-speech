import requests
import time

# Define the base URL for the server
BASE_URL = 'http://localhost:5008'

def test_start_transcribing():
    response = requests.post(f'{BASE_URL}/start')
    print(response.json())

def test_stop_transcribing():
    response = requests.post(f'{BASE_URL}/stop')
    print(response.json())

def test_get_status():
    response = requests.get(f'{BASE_URL}/status')
    print(response.json())

if __name__ == "__main__":
    # Test starting
    print("Starting transcribing...")
    test_start_transcribing()

    # Wait for a while to simulate some transcribing time
    time.sleep(5)

    # Test stopping transcribing
    print("\nStopping transcribing...")
    test_stop_transcribing()

    # Test getting transcribing status
    print("\nGetting transcribing status...")
    test_get_status()
