import tiktoken

def count_tokens(text):
    """Count the number of tokens in a given text using tiktoken.
    
    Args:
        text: The text to count tokens for
        
    Returns:
        int: Number of tokens in the text
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
