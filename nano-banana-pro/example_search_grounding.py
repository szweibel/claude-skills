#!/usr/bin/env python3
"""
Search Grounding Example
Demonstrates real-time data integration using Google Search
"""

import os
from google import genai
from google.genai import types

def generate_with_search():
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Prompt that requires real-time data
    prompt = """
    Create a professional infographic showing the current weather forecast
    for San Francisco for the next 3 days. Include temperature, conditions,
    and weather icons. Use a modern, clean design with blue and white colors.
    """

    print("Generating infographic with real-time weather data...")
    print("(Using Google Search grounding)\n")

    # Generate with search grounding enabled
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            tools=[{"google_search": {}}]  # Enable search grounding
        )
    )

    # Print the text response (shows what data was found)
    if response.text:
        print(f"Search findings: {response.text}\n")

    # Save the generated image (access via candidates)
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data:
                output_path = "weather_infographic.png"
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"✓ Infographic saved to {output_path}")
                print("  (Contains current real-time weather data)")
                return output_path

    print("✗ No image generated")
    return None

if __name__ == "__main__":
    generate_with_search()
