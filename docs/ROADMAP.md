# ScribeMaster Development Roadmap

> **Forked and evolved from LibriScribe** | AI-Powered Book Writing Suite
>
> Last Updated: 2025-12-07

## Vision

ScribeMaster is an AI-powered book writing platform that produces rich, context-aware narratives through structured workflows, comprehensive world/character codexes, and multi-agent collaboration. Unlike one-shot book generators, ScribeMaster maintains deep context continuity, validates factual grounding, and enables iterative refinement.

---

## Current State (v0.1.0)

### What Works
- 12+ specialized agents (concept, outline, character, worldbuilding, chapter writing, editing, etc.)
- Multi-LLM support (OpenAI, Anthropic, Google, DeepSeek, Mistral, OpenRouter)
- External YAML prompt templates
- Basic context continuity (previous chapter injection)
- Two workflow modes (Simple & Advanced)
- JSON-based knowledge base with Pydantic models

### Active Book Project
- **"When the Lights Learned to Lie"** - YA Dystopian
- 15/24 chapters written
- Chapters 1 & 2 recently revised with improved context system
- Rich worldbuilding and 6 developed characters

### Local Enhancements (Uncommitted)
- `context_manager.py` - Previous chapter context injection
- Scene title extraction in editor
- Enhanced project manager with validation
- CLI refactoring with language support
- Chapter review tracking

---

## Epic Overview

| Epic | Focus | Priority | Status |
|------|-------|----------|--------|
| **E0: Foundation** | GitHub setup, commit local changes, rebrand | Immediate | Pending |
| **E1: Enhanced Codex** | Rich character/scene/emotion tracking | High | Pending |
| **E2: Context Workflows** | PopKit-style flows, pre-write context assembly | High | Pending |
| **E3: Factual Grounding** | Historical/tech validation, research integration | Medium | Pending |
| **E4: Book Completion** | Finish The Remnant Code (Ch 16-24) | Parallel | In Progress |
| **E5: Review & Polish** | Revision workflows, consistency checks | Medium | Pending |
| **E6: Semantic Search** | Vector embeddings, query-based retrieval | Future | Planned |
| **E7: User Interface** | CLI commands, terminal UI, web dashboard | Future | Planned |

---

## Epic 0: Foundation (Immediate)

**Goal:** Establish ScribeMaster as your own project with version control.

### Tasks

#### 0.1 Create GitHub Repository
- Create `scribemaster` repo on your GitHub account
- Initialize with current code (including local changes)
- Add appropriate license (MIT or Apache 2.0)
- Update README with ScribeMaster branding

#### 0.2 Preserve Attribution
- Keep original LibriScribe acknowledgment in README
- Note it's "forked and evolved from guerra2fernando/libriscribe"
- Standard open source practice

#### 0.3 Rebrand Core Files
- Rename package from `libriscribe` to `scribemaster`
- Update CLI entry point
- Update import paths
- Update documentation references

#### 0.4 Commit Local Changes
- Stage all modified files
- Commit context_manager.py and related enhancements
- Tag as v0.1.0-alpha

#### 0.5 Project Structure
```
scribemaster/
├── src/scribemaster/
│   ├── agents/
│   ├── utils/
│   ├── codex/          # NEW: Enhanced knowledge system
│   ├── workflows/      # NEW: PopKit-style flows
│   └── validation/     # NEW: Fact-checking integration
├── prompts/templates/
├── projects/
├── docs/
│   ├── ROADMAP.md
│   ├── CLAUDE.md       # For Claude Code integration
│   └── ...
└── tests/
```

---

## Epic 1: Enhanced Codex System

**Goal:** Build rich, queryable knowledge structures for characters, scenes, emotions, and memories.

### 1.1 Character Codex Expansion

**Current:** Basic character profile (name, age, traits, background, arc)

**Enhanced:**
```python
class CharacterCodex:
    # Identity
    name: str
    aliases: List[str]
    age_at_chapter: Dict[int, int]  # Track aging through story

    # Appearance
    physical_description: str
    distinguishing_features: List[str]
    clothing_style: str

    # Psychology
    personality_traits: List[str]
    core_values: List[str]
    fears: List[str]
    desires: List[str]
    secrets: List[str]

    # Voice
    speech_patterns: str
    catchphrases: List[str]
    vocabulary_level: str

    # Relationships
    relationships: Dict[str, Relationship]  # character_name -> relationship
    relationship_evolution: List[RelationshipChange]  # Track changes

    # Arc
    arc_type: str  # e.g., "redemption", "fall", "coming-of-age"
    arc_milestones: List[ArcMilestone]

    # Emotional Journey
    emotional_states: Dict[int, List[Emotion]]  # chapter -> emotions
    memories: List[Memory]
    traumas: List[Trauma]
    growth_moments: List[GrowthMoment]
```

### 1.2 Scene Codex

**Track every scene with rich metadata:**
```python
class SceneCodex:
    scene_id: str
    chapter: int
    scene_number: int

    # Setting
    location: str
    time_of_day: str
    weather: str
    sensory_details: Dict[str, str]  # sight, sound, smell, touch, taste

    # Characters
    present_characters: List[str]
    pov_character: str
    character_emotions: Dict[str, Emotion]

    # Narrative
    scene_type: str  # action, dialogue, reflection, flashback, etc.
    conflict: str
    stakes: str
    outcome: str

    # Continuity
    items_mentioned: List[str]
    facts_established: List[str]
    promises_made: List[str]  # Chekhov's guns
    callbacks: List[str]  # References to earlier scenes

    # Themes
    themes_present: List[str]
    symbols_used: List[str]
    motifs: List[str]
```

### 1.3 Emotion Tracking

```python
class EmotionTracker:
    character: str
    emotion: str  # joy, fear, anger, sadness, hope, despair, etc.
    intensity: float  # 0.0 - 1.0
    trigger: str
    chapter: int
    scene: int

    # For arc tracking
    emotional_arc: List[EmotionPoint]  # emotion trajectory through story
```

### 1.4 Memory & Callback System

```python
class Memory:
    owner: str  # character who holds this memory
    content: str
    emotional_weight: str
    chapter_introduced: int
    chapters_referenced: List[int]

class Callback:
    setup_chapter: int
    setup_description: str
    payoff_chapter: Optional[int]
    payoff_description: Optional[str]
    status: str  # "planted", "paid_off", "abandoned"
```

### 1.5 Knowledge Base Migration
- Extend existing `ProjectKnowledgeBase` with new codex classes
- Maintain backward compatibility with existing projects
- Add migration script for The Remnant Code data

---

## Epic 2: Context Workflows

**Goal:** Implement PopKit-style flows that ensure full context before any writing/editing decision.

### 2.1 Pre-Write Context Assembly

Before writing any scene:
1. Load chapter outline and scene summary
2. Load all present characters' current states
3. Load previous scene summary (for continuity)
4. Load relevant emotional arcs
5. Load any pending callbacks that might be referenced
6. Load worldbuilding details for the setting
7. Assemble into structured context prompt

### 2.2 Workflow Commands

```bash
# Review current context before writing
scribemaster context show --chapter 16 --scene 1

# Validate continuity before writing
scribemaster validate continuity --chapter 16

# Write with full context
scribemaster write chapter 16 --context-aware

# Review and iterate
scribemaster review chapter 16 --check consistency

# Update codex after writing
scribemaster codex update --from chapter 16
```

### 2.3 Agent Orchestration Flow

```
User Request: "Write Chapter 16"
         ↓
[Context Assembler] ← gathers all relevant data
         ↓
[Continuity Validator] ← checks for conflicts
         ↓
[Chapter Writer Agent] ← writes with full context
         ↓
[Content Reviewer Agent] ← checks for issues
         ↓
[Codex Updater] ← extracts new facts/emotions
         ↓
User Review & Feedback
```

### 2.4 Configuration-Driven Workflows

```yaml
# workflows/write_chapter.yml
name: write_chapter
steps:
  - agent: context_assembler
    inputs: [chapter_number, scene_outlines, characters]

  - agent: continuity_validator
    inputs: [context, previous_chapters]
    checkpoint: true  # User approval before continuing

  - agent: chapter_writer
    inputs: [context, outline, style_guide]

  - agent: content_reviewer
    inputs: [draft, context, outline]

  - agent: codex_updater
    inputs: [approved_chapter, codex]
```

---

## Epic 3: Factual Grounding

**Goal:** Validate technological, historical, and real-world facts in the narrative.

### 3.1 Fact Registry

For The Remnant Code specifically:
- AI timeline (AlphaGo 2016, GPT-3 2020, DALL-E 2021, etc.)
- Starlink technology and capabilities
- Neural interface research state
- Texas geography and culture
- Christian scripture references

```python
class FactRegistry:
    category: str  # "technology", "history", "geography", "scripture", etc.
    fact: str
    source: str
    verification_date: date
    used_in_chapters: List[int]
```

### 3.2 Research Agent Enhancement

- Add structured fact extraction
- Source citation tracking
- Confidence scoring
- Integration with web search for verification

### 3.3 Fact-Check Workflow

```
Before Writing:
1. Extract claims that will be made in scene
2. Cross-reference with fact registry
3. Flag unverified claims
4. Research and verify new facts
5. Update registry

After Writing:
1. Scan chapter for factual claims
2. Validate against registry
3. Flag inconsistencies
4. Suggest corrections
```

---

## Epic 4: Book Completion (Parallel Track)

**Goal:** Finish "When the Lights Learned to Lie" (Chapters 16-24)

### Chapter Workflow (Per Chapter)

1. **Pre-Write Review**
   - Read chapter outline
   - Review character states at end of Ch 15
   - Check pending callbacks
   - Note emotional arcs to continue

2. **Scene-by-Scene Writing**
   - Full context injection per scene
   - Maintain emotional continuity
   - Honor established facts and callbacks

3. **Post-Write Review**
   - Consistency check
   - Codex update
   - User critique integration

### Chapters Remaining

| Chapter | Title | Act | Key Events | Status |
|---------|-------|-----|------------|--------|
| 16 | Embers of the Unscraped | II | Full astrolabe reassembly | Pending |
| 17 | Road of Milk and Honey | III | Journey begins | Pending |
| 18 | Thorns in the Flesh | III | Ruth's baby born | Pending |
| 19 | Rivers of Living Wire | III | Building wire-bridge | Pending |
| 20 | Betrayer's Lament | III | Redemption arc | Pending |
| 21 | Peaks of False Prophets | III | Shattering prophet core | Pending |
| 22 | Valleys of Decision | III | Path vote | Pending |
| 23 | Homeward, Third Moon's End | III | Third moon plummets | Pending |
| 24 | Souls Unowned, Christ Reigns | III | Arrival at refuge | Pending |

---

## Epic 5: Review & Polish

**Goal:** Revision workflows for completed chapters.

### 5.1 Consistency Checker

- Character trait consistency
- Timeline validation
- Location/geography consistency
- Object tracking (what's in the astrolabe?)
- Relationship evolution accuracy

### 5.2 Style Editor Enhancement

- Voice consistency per character
- Prose rhythm analysis
- Show vs. tell balance
- Pacing evaluation

### 5.3 Revision Workflow

```bash
scribemaster revise chapter 3 \
  --feedback "Caleb's fear feels underwritten" \
  --preserve-structure \
  --enhance-emotions
```

---

## Epic 6: Semantic Search (Future)

**Goal:** Vector embeddings for rich, query-based retrieval.

### 6.1 Embedding Strategy
- Embed scenes, not just chapters
- Embed character emotional states
- Embed worldbuilding facts
- Use local models (sentence-transformers) or API (OpenAI embeddings)

### 6.2 Query Examples
```bash
scribemaster query "scenes where Caleb feels hopeless"
scribemaster query "mentions of the astrolabe"
scribemaster query "Mara and Theo interactions"
scribemaster query "scripture references"
```

### 6.3 Implementation (Based on PopKit Pattern)
- Use existing PopKit embedding approach as reference
- ChromaDB or similar for local vector store
- Rate limiting and incremental updates

---

## Epic 7: User Interface (Future)

**Goal:** Enhanced CLI and eventual web dashboard.

### 7.1 Enhanced CLI
- Interactive mode with rich prompts
- Progress visualization
- Chapter preview panes
- Codex browsing commands

### 7.2 Terminal UI (TUI)
- Rich-based terminal interface
- Split panes for outline/writing/codex
- Real-time context display

### 7.3 Web Dashboard (Long-term)
- React-based project management
- Visual chapter/scene navigator
- Character relationship graphs
- Progress tracking

---

## Development Principles

### From Your Insights

1. **Context is King** - Never write without full context assembled
2. **Slow is Fast** - Methodical approach beats rapid iteration
3. **Structured Data** - Rich, segmented details enable rich storytelling
4. **Ground in Truth** - Fiction should be believable and fact-checked
5. **Review Everything** - Check before changing, verify after

### PopKit-Inspired Patterns

- Workflow-driven development
- Agent orchestration with checkpoints
- User approval gates
- Iterative refinement loops
- Configuration over code where sensible

---

## Immediate Next Steps

1. **Create GitHub repo** (`scribemaster`)
2. **Commit current changes** with proper structure
3. **Start Epic 1.1** (Character Codex expansion)
4. **Resume book** with Chapter 16 using enhanced context
5. **Document critiques** as they arise for future features

---

## Success Metrics

- **Book Completion:** 24/24 chapters written
- **Codex Richness:** Full character/scene/emotion tracking
- **Context Coverage:** 100% pre-write context assembly
- **Factual Accuracy:** All claims verified
- **User Satisfaction:** Narrative reads as cohesive, connected story

---

*This roadmap is a living document. Update as discoveries are made during book writing.*
