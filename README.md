# ScribeMaster

AI-Powered Book Writing Suite

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

> **Forked and evolved from [LibriScribe](https://github.com/guerra2fernando/libriscribe)** by Fernando Guerra

## Overview

ScribeMaster is an AI-powered book writing platform that produces rich, context-aware narratives through structured workflows, comprehensive world/character codexes, and multi-agent collaboration.

Unlike one-shot book generators, ScribeMaster:
- **Maintains deep context continuity** - Previous chapters inform current writing
- **Tracks character emotions and arcs** through a rich codex system
- **Validates factual grounding** - Fiction stays believable
- **Enables iterative refinement** - Review, critique, improve

## Features

### Creative Assistance
- **Concept Generation:** Transform ideas into detailed book concepts
- **Automated Outlining:** Create comprehensive chapter-by-chapter outlines
- **Character Generation:** Develop rich, multidimensional character profiles
- **Worldbuilding:** Craft detailed universes with history, culture, and geography

### Writing & Editing
- **Context-Aware Chapter Writing:** Generate chapters with full narrative context
- **Content Review:** Catch inconsistencies and plot holes
- **Style Editing:** Polish writing for target audience
- **Fact-Checking:** Verify claims for grounded fiction

### Quality Assurance
- **Plagiarism Detection:** Ensure content originality
- **Research Assistant:** Comprehensive topic research
- **Manuscript Formatting:** Export to Markdown or PDF

## Quick Start

### Installation

```bash
git clone https://github.com/jrc1883/scribemaster.git
cd scribemaster
pip install -e .
```

### Configuration

Get an API key from one of the supported providers:
- [OpenAI](https://platform.openai.com/signup/)
- [Anthropic Claude](https://console.anthropic.com/)
- [Google AI Studio (Gemini)](https://aistudio.google.com/)
- [OpenRouter](https://openrouter.ai/)
- [DeepSeek](https://platform.deepseek.com/)
- [Mistral AI](https://console.mistral.ai/)

Create a `.env` file:
```bash
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here
GOOGLE_AI_STUDIO_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
```

### Launch

```bash
scribemaster start
```

Choose between:
- **Simple Mode:** Quick, streamlined book creation
- **Advanced Mode:** Fine-grained control over each step

## Core Commands

```bash
# Start interactive session
scribemaster start

# Generate book concept
scribemaster concept

# Create outline
scribemaster outline

# Generate characters
scribemaster characters

# Build world
scribemaster worldbuilding

# Write chapter with context
scribemaster write-chapter --chapter-number 1

# Edit chapter
scribemaster edit-chapter --chapter-number 1

# Format book
scribemaster format
```

## Project Structure

```
your_project/
├── project_data.json    # Full project knowledge base
├── outline.md           # Book outline
├── characters.json      # Character profiles
├── world.json           # Worldbuilding details
├── scenes.json          # Scene breakdowns
├── chapter_1.md         # Generated chapters
├── chapter_2.md
└── manuscript.md        # Compiled manuscript
```

## Development Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full development plan.

### Current Epics
- **E0: Foundation** - GitHub setup, branding (Complete)
- **E1: Enhanced Codex** - Rich character/scene/emotion tracking
- **E2: Context Workflows** - PopKit-style flows with full context
- **E3: Factual Grounding** - Historical/tech validation
- **E4: Book Completion** - Finish active book project
- **E5: Review & Polish** - Revision workflows
- **E6: Semantic Search** - Vector embeddings (Future)
- **E7: User Interface** - CLI/Web dashboard (Future)

## Attribution

This project is forked from and builds upon [LibriScribe](https://github.com/guerra2fernando/libriscribe) by Fernando Guerra and Lenxys. We gratefully acknowledge their foundational work on the multi-agent book writing system.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made by jrc1883 | Built on LibriScribe
