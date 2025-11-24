#!/usr/bin/env python3
"""
Iterative Refinement Example
Demonstrates multi-turn conversation for progressive image refinement
"""

import os
from google import genai
from google.genai import types

def save_image(response, filename):
    """Helper to save image from response"""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data:
                with open(filename, "wb") as f:
                    f.write(part.inline_data.data)
                return True
    return False

def iterative_refinement():
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Start a chat session for iterative refinement
    print("Starting iterative refinement session...\n")

    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
        )
    )

    # Step 1: Initial generation
    print("Step 1: Generating initial logo...")
    response1 = chat.send_message(
        "Create a minimalist logo for a tech startup called 'CloudFlow' "
        "that specializes in cloud computing solutions"
    )
    if response1.text:
        print(f"Response: {response1.text}\n")

    # Save version 1
    if save_image(response1, "cloudflow_v1.png"):
        print("✓ Version 1 saved as cloudflow_v1.png\n")

    # Step 2: First refinement
    print("Step 2: Refining colors...")
    response2 = chat.send_message(
        "Make the colors more vibrant - use a gradient from deep blue to cyan"
    )
    if response2.text:
        print(f"Response: {response2.text}\n")

    # Save version 2
    if save_image(response2, "cloudflow_v2.png"):
        print("✓ Version 2 saved as cloudflow_v2.png\n")

    # Step 3: Second refinement
    print("Step 3: Adjusting typography...")
    response3 = chat.send_message(
        "Change the font to a modern sans-serif, bold weight, and add subtle "
        "cloud icon integrated into the letter 'C'"
    )
    if response3.text:
        print(f"Response: {response3.text}\n")

    # Save final version
    if save_image(response3, "cloudflow_final.png"):
        print("✓ Final version saved as cloudflow_final.png")

    print("\n✓ Iterative refinement complete!")
    print("  Generated 3 versions: v1, v2, and final")

if __name__ == "__main__":
    iterative_refinement()
