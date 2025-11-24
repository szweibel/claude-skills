# Nano Banana Pro Skill

A comprehensive Claude Code skill for using Google's Nano Banana Pro (Gemini 3 Pro Image) API - the state-of-the-art AI image generation model.

## What This Skill Provides

- **Complete API Documentation** - Setup, authentication, and usage examples
- **Code Examples** - Python scripts demonstrating key features
- **Prompting Best Practices** - Templates and guidelines for effective prompts
- **Advanced Features** - 4K generation, search grounding, multi-image support

## Quick Start

### 1. Get Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com)
2. Sign in and click "Get API key"
3. **Enable billing** (required for Nano Banana Pro)

### 2. Set Up Environment

```bash
cd ~/.claude/skills/nano-banana-pro
cp .env.example .env
# Edit .env and add your API key
```

### 3. Install Dependencies

```bash
pip install google-genai pillow
```

### 4. Run Examples

```bash
# Basic generation
python example_basic.py

# 4K high-resolution
python example_high_res.py

# Iterative refinement
python example_iterative.py

# Search-grounded generation
python example_search_grounding.py
```

## Files Included

- **SKILL.md** - Complete skill documentation with API usage and prompting guide
- **.env.example** - Template for environment variables
- **example_basic.py** - Simple text-to-image generation
- **example_high_res.py** - 4K image generation with custom aspect ratios
- **example_iterative.py** - Multi-turn conversation for progressive refinement
- **example_search_grounding.py** - Real-time data integration via Google Search
- **README.md** - This file

## Key Features

### Nano Banana Pro vs Flash

| Feature | Pro (Gemini 3) | Flash (Gemini 2.5) |
|---------|---------------|-------------------|
| Max Resolution | 4K | 1024px |
| Search Grounding | ✅ | ❌ |
| "Thinking" Process | ✅ | ❌ |
| Cost (2K) | ~$0.134 | Lower |

### When to Use Pro vs Flash

**Use Pro for:**
- Professional print materials (4K needed)
- Text-heavy designs (logos, posters)
- Search-grounded infographics
- Complex compositions requiring "thinking"

**Use Flash for:**
- Rapid prototyping
- High-volume generation
- Cost-sensitive projects
- 1024px resolution sufficient

## Resources

- **Skill Documentation**: See [SKILL.md](SKILL.md)
- **Official API Docs**: https://ai.google.dev/gemini-api/docs/image-generation
- **Google AI Studio**: https://aistudio.google.com
- **Pricing**: https://ai.google.dev/pricing

## Usage with Claude Code

Once installed, Claude Code can reference this skill for:

1. **API Integration** - Implementing Nano Banana Pro in your applications
2. **Prompt Crafting** - Writing effective image generation prompts
3. **Feature Guidance** - Understanding capabilities and limitations
4. **Code Examples** - Ready-to-use templates for common tasks

## Troubleshooting

### "API key not set"
- Make sure you've created `.env` file from `.env.example`
- Set `GOOGLE_API_KEY` environment variable

### "Billing not enabled"
- Nano Banana Pro requires paid access
- Enable billing in Google AI Studio

### "Rate limit exceeded"
- Check your quota in AI Studio
- Consider using Batch API for large workloads

## License

This skill documentation is provided as-is for use with Claude Code.

Google Gemini API usage is subject to [Google's Terms of Service](https://ai.google.dev/gemini-api/terms).

---

**Last Updated:** November 2025
**Skill Version:** 1.0.0
