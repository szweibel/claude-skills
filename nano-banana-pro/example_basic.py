#!/usr/bin/env python3
"""
Basic Nano Banana Pro Example
Generates a simple image from a text prompt
"""

import os
from google import genai
from google.genai import types

def generate_basic_image():
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Your prompt
    prompt = """
    Wide-angle shot of a cozy coffee shop interior at golden hour,
    warm sunlight streaming through large windows, vintage furniture,
    customers reading books, barista preparing coffee in the background,
    atmospheric and inviting mood. Shot on Canon 5D with 24mm lens.
    """

    print("Generating image...")

    # Generate image
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    # Save the generated image (access via candidates)
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data:
                output_path = "coffee_shop.png"
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"✓ Image saved to {output_path}")
                return output_path

    print("✗ No image generated")
    return None

if __name__ == "__main__":
    generate_basic_image()
