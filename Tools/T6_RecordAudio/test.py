import requests
import time

# Define the base URL for the server
BASE_URL = 'http://localhost:5006'

def test_start_recording():
    response = requests.post(f'{BASE_URL}/start')
    print(response.json())

def test_stop_recording():
    response = requests.post(f'{BASE_URL}/stop')
    print(response.json())

def test_get_recording_status():
    response = requests.get(f'{BASE_URL}/status')
    print(response.json())

if __name__ == "__main__":
    # Test starting recording
    print("Starting recording...")
    test_start_recording()

    # Wait for a while to simulate some recording time
    time.sleep(16)

    # Test stopping recording
    print("\nStopping recording...")
    test_stop_recording()

    # Test getting recording status
    print("\nGetting recording status...")
    test_get_recording_status()
