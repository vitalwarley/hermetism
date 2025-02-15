#!/usr/bin/env python3

from openai import OpenAI
import os

def check_model():
    if 'OPENAI_API_KEY' not in os.environ:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return

    client = OpenAI()
    
    try:
        # Try to create a simple completion with the model
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hello, are you available?"}
                    ]
                }
            ],
            max_tokens=10
        )
        print("✅ gpt-4-turbo-preview model is available!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print("❌ Error checking model availability:")
        print(f"Error message: {str(e)}")

if __name__ == "__main__":
    check_model() 