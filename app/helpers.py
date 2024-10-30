import requests, random

def is_word_valid(input: str) -> bool:
    """Gets an input and sends a request to dictionaryapi.dev to check if it is a valid word."""
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{input}")
        response.raise_for_status()  # Raise an error for unsuccessful requests
        word = response.json()[0]["word"]
        return bool(word)
    except requests.exceptions.RequestException:
        return False

def get_random_word() -> str:
    """Gets a random common 5-letter word from the Datamuse API."""
    try:
        response = requests.get("https://api.datamuse.com/words?sp=?????&max=1000&md=f")
        response.raise_for_status()
        words = [
            word['word'] for word in response.json()
            if 'tags' in word and 'f:' in word['tags'][0] and float(word['tags'][0][2:]) > 5
        ]

        if words:
            return random.choice(words)
        else:
            raise ValueError("No common words found in response.")
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching random word: {e}")
        return ""
    
if __name__ == "__main__":
    x = get_random_word()
    print(is_word_valid(x))