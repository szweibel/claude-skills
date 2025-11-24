# Nano Banana Pro (Gemini 3 Pro Image) - API Usage & Prompting Guide

Build powerful image generation and editing applications using Google's Nano Banana Pro (Gemini 3 Pro Image), the state-of-the-art AI image model released November 2025.

## Overview

**Nano Banana Pro** (officially `gemini-3-pro-image-preview`) is Google's most advanced image generation model, offering:

- **4K Resolution Output** - Print-quality images up to 4K
- **Advanced "Thinking"** - Built-in reasoning for complex compositions
- **Search Grounding** - Real-time data integration via Google Search
- **Multi-Image Support** - Up to 14 reference images in a single generation
- **Accurate Text Rendering** - High-fidelity text in multiple languages
- **Multi-Turn Conversations** - Iterative refinement through chat

### Model Comparison

| Feature | Gemini 3 Pro Image (Pro) | Gemini 2.5 Flash Image (Flash) |
|---------|-------------------------|--------------------------------|
| Model ID | `gemini-3-pro-image-preview` | `gemini-2.5-flash-image` |
| Max Resolution | 4K | 1024px |
| Search Grounding | ✅ Yes | ❌ No |
| Thinking Process | ✅ Yes | ❌ No |
| Reference Images | Up to 14 | Up to 14 |
| Speed | Slower, higher quality | Faster, cost-effective |
| Cost (2K) | ~$0.134 | Lower |
| Cost (4K) | ~$0.24 | N/A |

## Setup & Installation

### 1. Get API Key

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API key" in the left sidebar
4. **Enable billing** (Nano Banana Pro requires paid access)
5. Copy your API key

### 2. Install SDK

**Python:**
```bash
pip install google-genai
```

**JavaScript/Node.js:**
```bash
npm install @google/genai
```

### 3. Set Environment Variable

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
GOOGLE_API_KEY=your-api-key-here
```

## API Usage Examples

### Basic Text-to-Image (Python)

```python
from google import genai
from google.genai import types

# Initialize client
client = genai.Client(api_key="YOUR_API_KEY")

# Generate image
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["A futuristic cityscape at sunset with flying cars, photorealistic, 4K quality"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

# Save the generated image (access via candidates)
for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
            with open("cityscape.png", "wb") as f:
                f.write(part.inline_data.data)
            print("Image saved!")
```

### Basic Text-to-Image (JavaScript)

```javascript
const { GoogleGenAI } = require("@google/genai");

const ai = new GoogleGenAI({ apiKey: process.env.GOOGLE_API_KEY });

async function generateImage() {
    const response = await ai.models.generateContent({
        model: "gemini-3-pro-image-preview",
        contents: ["A futuristic cityscape at sunset with flying cars, photorealistic, 4K quality"],
    });

    // Process response
    for (const part of response.parts) {
        if (part.inlineData) {
            // Save or process image data
            const imageBuffer = Buffer.from(part.inlineData.data, 'base64');
            require('fs').writeFileSync('cityscape.png', imageBuffer);
            console.log("Image saved!");
        }
    }
}

generateImage();
```

### High-Resolution Output (2K/4K)

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["Professional product photography of a luxury watch on marble surface"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="4K"  # Options: "1K", "2K", "4K"
        )
    )
)

for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
            with open("watch_4k.png", "wb") as f:
                f.write(part.inline_data.data)
```

### Image Editing

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

# Load your existing image
original_image = Image.open("photo.jpg")

# Edit with text prompt
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "Add a rainbow in the sky and make the colors more vibrant",
        original_image
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
            with open("edited_photo.png", "wb") as f:
                f.write(part.inline_data.data)
```

### Multi-Turn Conversation (Iterative Refinement)

```python
from google import genai
from google.genai import types

client = genai.Client()

# Start a chat session for iterative refinement
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)

# First generation
response1 = chat.send_message("Create a logo for a tech startup called 'NeuralNet'")
print(f"Response 1: {response1.text}")

# Refine the image
response2 = chat.send_message("Make the colors more vibrant and add a neural network pattern in the background")
print(f"Response 2: {response2.text}")

# Further refinement
response3 = chat.send_message("Change the font to something more modern and bold")

# Save final image
for candidate in response3.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
            with open("neuralnet_logo_final.png", "wb") as f:
                f.write(part.inline_data.data)
```

### Search Grounding (Real-Time Data)

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["Create an infographic showing the current weather in New York City"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        tools=[{"google_search": {}}]  # Enable search grounding
    )
)

for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
            with open("nyc_weather.png", "wb") as f:
                f.write(part.inline_data.data)
```

### Multiple Reference Images (Up to 14)

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

# Load reference images
ref_image1 = Image.open("style_reference.jpg")
ref_image2 = Image.open("character_reference.jpg")
ref_image3 = Image.open("background_reference.jpg")

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "Create a new scene combining the art style from the first image, "
        "the character from the second image, and the background atmosphere "
        "from the third image",
        ref_image1,
        ref_image2,
        ref_image3
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
            with open("combined_scene.png", "wb") as f:
                f.write(part.inline_data.data)
```

### Batch Image Generation

For large-scale production with up to 24-hour turnaround (50% cost savings):

```python
from google import genai

client = genai.Client()

# Upload batch requests file (JSONL format)
uploaded_file = client.files.upload(path="batch_requests.jsonl")

# Create batch job
file_batch_job = client.batches.create(
    model="gemini-2.5-flash-image",
    src=uploaded_file.name,
)

print(f"Batch job created: {file_batch_job.name}")

# Check status later
job = client.batches.get(name=file_batch_job.name)
print(f"Status: {job.state}")
```

## Prompting Best Practices

### Core Principle
**"Describe the scene, don't just list keywords."**

Use flowing narrative descriptions with context rather than keyword lists.

### Template 1: Photorealistic Scenes

```
[Shot Type] of [Subject] in [Environment], [Lighting], [Mood/Atmosphere].
Shot on [Camera] with [Lens], [Additional Details].

Example:
"Wide-angle shot of a chef preparing pasta in a modern restaurant kitchen,
warm golden hour lighting streaming through industrial windows, energetic
and professional atmosphere. Shot on Sony A7IV with 24mm f/1.4 lens,
shallow depth of field, steam rising from the pot."
```

### Template 2: Stylized Illustrations & Stickers

```
[Art Style] illustration of [Subject], [Characteristics], [Color Palette],
[Additional Style Notes].

Example:
"Kawaii-style sticker illustration of a smiling coffee cup with big eyes,
chibi proportions, pastel pink and brown color palette, white outline,
glossy finish, cute and friendly expression."
```

### Template 3: Text-Heavy Designs (Logos, Posters)

```
[Design Type] for [Brand/Concept], [Text Content], [Font Style],
[Color Scheme], [Layout].

Example:
"Modern minimalist logo for 'CloudFlow' SaaS company, sans-serif typeface
with flowing cloud icon integrated into the 'C', blue and white gradient
color scheme, clean and professional."
```

**Note:** Keep overlaid text under 25 characters for best accuracy.

### Template 4: Product Photography

```
[Shot Type] product photography of [Product] on [Surface/Background],
[Lighting Setup], [Angle], [Mood].

Example:
"Hero shot product photography of wireless headphones on white marble
surface, studio lighting with soft key light and rim light highlighting
edges, 45-degree angle, premium and modern aesthetic."
```

### Template 5: Minimalist Design

```
Minimalist [Design Type] featuring [Single Subject], [Composition],
[Color Palette], [Negative Space].

Example:
"Minimalist poster design featuring a single red umbrella, centered
composition with rule of thirds, black and red color palette,
abundant white negative space creating elegant simplicity."
```

## Advanced Features

### Character Consistency (Up to 5 Characters)

Maintain the same characters across multiple generations:

```python
# First generation - establish character
response1 = chat.send_message("Create a character: a friendly robot with blue eyes")

# Subsequent generations maintain consistency
response2 = chat.send_message("Show the same robot character waving hello")
response3 = chat.send_message("Show the same robot in a different pose, reading a book")
```

### Multilingual Text Generation

Generate text in multiple languages within images:

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "Create a welcome poster with 'Welcome' written in English, Spanish, "
        "French, and Japanese in a modern typographic layout"
    ],
)
```

### Aspect Ratio Control

```python
config=types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="16:9"  # Options: "1:1", "16:9", "9:16", "3:4", "4:3"
    )
)
```

## Pro Tips

### For Best Results:

1. **Be Specific** - Include details about lighting, camera angles, materials, mood
2. **Use Narrative Flow** - Write in sentences, not keyword lists
3. **One Change at a Time** - When editing, make incremental adjustments
4. **Leverage Search** - Use search grounding for real-world accuracy (weather, facts, current events)
5. **Iterate in Conversation** - Use multi-turn chat for progressive refinement
6. **Reference Real Cameras/Lenses** - "Shot on Canon 5D, 50mm f/1.8" produces more photorealistic results
7. **Specify Art Movements** - "in the style of Art Nouveau" or "cyberpunk aesthetic"
8. **Keep Text Short** - For text in images, stay under 25 characters for best accuracy

### What to Avoid:

- ❌ Vague requests like "make it better" or "improve this"
- ❌ Keyword lists: "sunset, beach, waves, colors, beautiful"
- ❌ Changing multiple elements simultaneously
- ❌ Overly long text overlays (>25 characters)
- ❌ Copyrighted characters or trademarked content

## Error Handling

```python
from google import genai
from google.genai import types

client = genai.Client()

try:
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=["Your prompt here"],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data:
                with open("output.png", "wb") as f:
                    f.write(part.inline_data.data)

except Exception as e:
    print(f"Error: {e}")
```

## Rate Limits & Quotas

- **Free Tier**: Not available for Nano Banana Pro
- **Paid Tier**: Standard rate limits apply (check current limits in AI Studio)
- **Batch API**: Higher limits with 24-hour turnaround, 50% cost savings

## Pricing (Approximate)

- **1K Resolution**: ~$0.134 per image
- **2K Resolution**: ~$0.134 per image
- **4K Resolution**: ~$0.24 per image
- **Batch API**: 50% discount on above prices

*Check [Google AI Pricing](https://ai.google.dev/pricing) for current rates.*

## Safety & Compliance

- All images include **SynthID watermarks** for authentication
- Respect copyright and intellectual property when using reference images
- Follow Google's [Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms)
- Generated images must not violate content policies

## Use Cases

### Professional Applications:
- 📊 **Data Visualization** - Infographics with search-grounded real-time data
- 🎨 **Marketing Assets** - High-resolution product mockups and promotional imagery
- 📝 **Document Design** - Technical diagrams, flowcharts with legible text
- 🎬 **Storyboarding** - Character-consistent scene generation
- 🏢 **Presentation Graphics** - Custom illustrations for slides and reports

### Creative Projects:
- 🖼️ **Concept Art** - Iterative refinement of artistic visions
- 🎮 **Game Assets** - Character designs with consistency across variations
- 📚 **Book Illustrations** - Story scenes with maintained character appearances
- 🌐 **Web Design** - Custom hero images and background assets

## Additional Resources

- **Official Documentation**: [ai.google.dev/gemini-api/docs/image-generation](https://ai.google.dev/gemini-api/docs/image-generation)
- **Google AI Studio**: [aistudio.google.com](https://aistudio.google.com)
- **Prompt Guide**: [ai.google.dev/gemini-api/docs/prompting-strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- **API Pricing**: [ai.google.dev/pricing](https://ai.google.dev/pricing)
- **Developer Forum**: [ai.google.dev/community](https://ai.google.dev/community)

## Quick Reference Card

```python
# Basic generation
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_KEY")

# Simple text-to-image
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["Your detailed prompt here"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

# With full configuration
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["Your prompt"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="4K"
        ),
        tools=[{"google_search": {}}]  # Enable search
    )
)

# Save image (access via candidates)
for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
            with open("output.png", "wb") as f:
                f.write(part.inline_data.data)
```

---

**Last Updated:** November 2025
**Model Version:** Gemini 3 Pro Image (gemini-3-pro-image-preview)
