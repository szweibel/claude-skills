#!/usr/bin/env python3
"""
High-Resolution Image Generation Example
Demonstrates 4K output with custom aspect ratio
"""

import os
from google import genai
from google.genai import types

def generate_4k_image():
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Professional product photography prompt
    prompt = """
    Hero shot product photography of a luxury smartwatch with black metal band
    on polished white marble surface, studio lighting with soft key light from
    the left and rim light highlighting the edges, 45-degree angle, premium
    and sophisticated aesthetic, reflections visible on marble, 4K quality.
    """

    print("Generating 4K image (this may take a moment)...")

    # Generate with 4K configuration
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",  # Cinematic aspect ratio
                image_size="4K"       # High resolution
            )
        )
    )

    # Save the generated image (access via candidates)
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data:
                output_path = "smartwatch_4k.png"
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"✓ 4K image saved to {output_path}")
                return output_path

    print("✗ No image generated")
    return None

if __name__ == "__main__":
    generate_4k_image()
