import re

def extract_numbers(text):
    numbers = re.findall(r'\b\d+\b', text)
    return numbers


if __name__ == "__main__":

    # Example usage:
    text = "The price is $25.99 and the quantity is 35467. Don't forget to call 1234567890."
    numbers = extract_numbers(text)
    print(numbers)  # Output: [25, 35467, 1234567890]