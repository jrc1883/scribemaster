# src/libriscribe/codex.py
"""
Enhanced Codex System for ScribeMaster

Rich, queryable knowledge structures for characters, scenes, emotions, and memories.
Designed for deep context continuity and narrative consistency tracking.
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


# =============================================================================
# ENUMERATIONS
# =============================================================================

class EmotionType(str, Enum):
    """Core emotions for character tracking"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    # Extended emotions
    HOPE = "hope"
    DESPAIR = "despair"
    LOVE = "love"
    GRIEF = "grief"
    GUILT = "guilt"
    SHAME = "shame"
    PRIDE = "pride"
    ANXIETY = "anxiety"
    PEACE = "peace"
    DETERMINATION = "determination"
    CONFUSION = "confusion"
    LONELINESS = "loneliness"


class RelationshipType(str, Enum):
    """Types of character relationships"""
    FAMILY = "family"
    FRIEND = "friend"
    RIVAL = "rival"
    ENEMY = "enemy"
    MENTOR = "mentor"
    STUDENT = "student"
    ROMANTIC = "romantic"
    ALLY = "ally"
    ACQUAINTANCE = "acquaintance"
    COMPLICATED = "complicated"


class SceneType(str, Enum):
    """Scene narrative types"""
    ACTION = "action"
    DIALOGUE = "dialogue"
    REFLECTION = "reflection"
    FLASHBACK = "flashback"
    DISCOVERY = "discovery"
    CONFRONTATION = "confrontation"
    ESCAPE = "escape"
    REUNION = "reunion"
    REVELATION = "revelation"
    TRANSITION = "transition"


class CallbackStatus(str, Enum):
    """Status of narrative callbacks (Chekhov's guns)"""
    PLANTED = "planted"
    REFERENCED = "referenced"
    PAID_OFF = "paid_off"
    ABANDONED = "abandoned"


class ArcType(str, Enum):
    """Character arc archetypes"""
    COMING_OF_AGE = "coming_of_age"
    REDEMPTION = "redemption"
    FALL = "fall"
    TRANSFORMATION = "transformation"
    FLAT = "flat"  # Character stays same, world changes
    DISILLUSIONMENT = "disillusionment"
    EDUCATION = "education"
    TESTING = "testing"


# =============================================================================
# EMOTION & PSYCHOLOGY MODELS
# =============================================================================

class EmotionState(BaseModel):
    """A character's emotional state at a specific moment"""
    emotion: EmotionType
    intensity: float = Field(ge=0.0, le=1.0, description="0.0 to 1.0 intensity scale")
    trigger: str = ""  # What caused this emotion
    expression: str = ""  # How it manifests (physical, verbal, etc.)

    class Config:
        use_enum_values = True


class EmotionalMoment(BaseModel):
    """An emotionally significant moment for a character"""
    chapter: int
    scene: int
    emotions: List[EmotionState] = []
    context: str = ""  # Brief description of what happened
    significance: str = ""  # Why this matters to the character


class PsychologicalProfile(BaseModel):
    """Deep psychological traits for a character"""
    core_values: List[str] = []  # What they believe in deeply
    fears: List[str] = []  # What terrifies them
    desires: List[str] = []  # What they want most
    secrets: List[str] = []  # What they hide from others
    beliefs: List[str] = []  # Worldview, philosophy, faith
    flaws: List[str] = []  # Character weaknesses
    strengths: List[str] = []  # Character strengths
    triggers: List[str] = []  # What sets them off emotionally


# =============================================================================
# RELATIONSHIP MODELS
# =============================================================================

class RelationshipState(BaseModel):
    """State of a relationship at a specific point"""
    chapter: int
    trust_level: float = Field(ge=0.0, le=1.0, default=0.5)
    affection_level: float = Field(ge=0.0, le=1.0, default=0.5)
    conflict_level: float = Field(ge=0.0, le=1.0, default=0.0)
    description: str = ""  # Current state description


class Relationship(BaseModel):
    """A relationship between two characters"""
    target_character: str  # The other character's name
    relationship_type: RelationshipType
    description: str = ""  # Nature of the relationship
    history: str = ""  # How they met, shared experiences
    dynamics: str = ""  # How they interact
    evolution: List[RelationshipState] = []  # How it changes over time

    class Config:
        use_enum_values = True


# =============================================================================
# MEMORY & CALLBACK MODELS
# =============================================================================

class Memory(BaseModel):
    """A significant memory held by a character"""
    id: str = ""  # Unique identifier
    owner: str  # Character who holds this memory
    content: str  # What the memory is about
    emotional_weight: EmotionType = EmotionType.SADNESS
    chapter_introduced: int = 0  # When first mentioned
    chapters_referenced: List[int] = []  # Where it comes up again
    associated_characters: List[str] = []  # Who else is involved
    is_trauma: bool = False
    is_positive: bool = False

    class Config:
        use_enum_values = True


class Callback(BaseModel):
    """A narrative promise/setup that should be paid off (Chekhov's gun)"""
    id: str = ""
    name: str  # Short identifier like "astrolabe_meaning"
    setup_chapter: int
    setup_scene: int = 0
    setup_description: str  # What was planted
    payoff_chapter: Optional[int] = None
    payoff_scene: Optional[int] = None
    payoff_description: Optional[str] = None
    status: CallbackStatus = CallbackStatus.PLANTED
    importance: str = "medium"  # low, medium, high, critical
    notes: str = ""

    class Config:
        use_enum_values = True


class FactEstablished(BaseModel):
    """A fact established in the narrative that must remain consistent"""
    id: str = ""
    fact: str  # The fact itself
    category: str = "general"  # character, world, tech, history, etc.
    chapter_established: int
    scene_established: int = 0
    chapters_referenced: List[int] = []
    source: str = ""  # Where this fact comes from (research, author, etc.)
    verified: bool = False
    notes: str = ""


# =============================================================================
# CHARACTER ARC MODELS
# =============================================================================

class ArcMilestone(BaseModel):
    """A significant milestone in a character's arc"""
    chapter: int
    scene: int = 0
    description: str
    growth_area: str = ""  # What aspect of character this affects
    before_state: str = ""  # How they were before
    after_state: str = ""  # How they are after
    catalyst: str = ""  # What caused the change


class CharacterVoice(BaseModel):
    """Character's unique voice and speech patterns"""
    speech_patterns: str = ""  # How they talk
    vocabulary_level: str = "average"  # simple, average, sophisticated, technical
    catchphrases: List[str] = []
    verbal_tics: List[str] = []  # "um", "like", etc.
    accent_notes: str = ""
    internal_monologue_style: str = ""  # How their thoughts are expressed


# =============================================================================
# ENHANCED CHARACTER CODEX
# =============================================================================

class CharacterCodex(BaseModel):
    """
    Enhanced character profile with deep tracking for emotions, relationships,
    memories, and arc progression.
    """
    # Identity
    name: str
    full_name: str = ""
    aliases: List[str] = []
    age_at_story_start: str = ""
    age_progression: Dict[int, str] = {}  # chapter -> age (for time jumps)

    # Appearance
    physical_description: str = ""
    distinguishing_features: List[str] = []
    clothing_style: str = ""
    physical_mannerisms: List[str] = []

    # Role
    role: str = ""  # protagonist, antagonist, supporting, etc.
    faction: str = ""  # Which group they belong to
    occupation: str = ""

    # Personality (from original)
    personality_traits: str = ""
    background: str = ""
    motivations: str = ""
    internal_conflicts: str = ""
    external_conflicts: str = ""
    character_arc: str = ""
    arc_type: ArcType = ArcType.TRANSFORMATION

    # Enhanced Psychology
    psychology: PsychologicalProfile = Field(default_factory=PsychologicalProfile)

    # Voice
    voice: CharacterVoice = Field(default_factory=CharacterVoice)

    # Relationships
    relationships: Dict[str, Relationship] = {}  # char_name -> Relationship

    # Emotional Journey
    emotional_journey: List[EmotionalMoment] = []
    dominant_emotions: List[EmotionType] = []  # Most common emotions for this char

    # Memories
    memories: List[Memory] = []

    # Arc Progression
    arc_milestones: List[ArcMilestone] = []

    # Scene Presence
    scenes_appeared: List[Tuple[int, int]] = []  # List of (chapter, scene) tuples
    pov_scenes: List[Tuple[int, int]] = []  # Scenes from their POV

    # Status tracking
    is_alive: bool = True
    death_chapter: Optional[int] = None
    current_location: str = ""
    inventory: List[str] = []  # Items they possess

    class Config:
        use_enum_values = True

    def add_emotional_moment(self, chapter: int, scene: int,
                             emotions: List[EmotionState],
                             context: str = "", significance: str = ""):
        """Add an emotional moment to the character's journey"""
        moment = EmotionalMoment(
            chapter=chapter,
            scene=scene,
            emotions=emotions,
            context=context,
            significance=significance
        )
        self.emotional_journey.append(moment)

    def get_emotions_at_chapter(self, chapter: int) -> List[EmotionalMoment]:
        """Get all emotional moments for a specific chapter"""
        return [m for m in self.emotional_journey if m.chapter == chapter]

    def get_relationship(self, character_name: str) -> Optional[Relationship]:
        """Get relationship with another character"""
        return self.relationships.get(character_name)

    def add_memory(self, memory: Memory):
        """Add a memory to the character"""
        self.memories.append(memory)

    def get_relevant_memories(self, chapter: int) -> List[Memory]:
        """Get memories introduced before or at this chapter"""
        return [m for m in self.memories if m.chapter_introduced <= chapter]


# =============================================================================
# ENHANCED SCENE CODEX
# =============================================================================

class SensoryDetails(BaseModel):
    """Sensory information for a scene"""
    sight: str = ""
    sound: str = ""
    smell: str = ""
    touch: str = ""
    taste: str = ""
    atmosphere: str = ""  # Overall mood/feeling


class SceneCodex(BaseModel):
    """
    Enhanced scene tracking with rich metadata for continuity and context.
    """
    # Identity
    scene_id: str = ""  # Unique ID like "ch3_sc2"
    chapter: int
    scene_number: int
    title: str = ""

    # From original
    summary: str = ""
    characters: List[str] = []
    setting: str = ""
    goal: str = ""
    emotional_beat: str = ""

    # Enhanced Setting
    location: str = ""
    time_of_day: str = ""
    weather: str = ""
    sensory_details: SensoryDetails = Field(default_factory=SensoryDetails)

    # Character States
    pov_character: str = ""
    character_emotions: Dict[str, List[EmotionState]] = {}  # char -> emotions
    character_goals: Dict[str, str] = {}  # char -> what they want in this scene

    # Narrative
    scene_type: SceneType = SceneType.ACTION
    conflict: str = ""
    stakes: str = ""
    outcome: str = ""
    tension_level: float = Field(ge=0.0, le=1.0, default=0.5)

    # Continuity
    items_mentioned: List[str] = []
    facts_established: List[str] = []  # New facts introduced
    facts_referenced: List[str] = []  # Existing facts mentioned
    callbacks_planted: List[str] = []  # Callback IDs
    callbacks_referenced: List[str] = []  # Callback IDs mentioned
    callbacks_resolved: List[str] = []  # Callback IDs paid off

    # Themes
    themes_present: List[str] = []
    symbols_used: List[str] = []
    motifs: List[str] = []
    scripture_references: List[str] = []  # For faith-based narratives

    # Connections
    leads_to: str = ""  # Next scene ID
    follows_from: str = ""  # Previous scene ID
    parallel_scenes: List[str] = []  # Related scenes for reference

    # Writing metadata
    word_count: int = 0
    draft_status: str = "draft"  # draft, revised, final
    notes: str = ""

    class Config:
        use_enum_values = True


# =============================================================================
# CHAPTER CODEX
# =============================================================================

class ChapterCodex(BaseModel):
    """Enhanced chapter tracking"""
    chapter_number: int
    title: str = ""
    summary: str = ""

    # Scenes
    scenes: List[SceneCodex] = []

    # Arc placement
    act: str = ""  # "Act I", "Act II", etc.
    arc_position: str = ""  # "inciting incident", "midpoint", "climax", etc.

    # Characters
    pov_characters: List[str] = []
    characters_appearing: List[str] = []
    character_focus: str = ""  # Primary character for this chapter

    # Themes
    primary_theme: str = ""
    secondary_themes: List[str] = []

    # Pacing
    tension_arc: str = ""  # Description of tension flow
    emotional_arc: str = ""  # Emotional journey through chapter

    # Continuity
    callbacks_in_chapter: List[str] = []
    facts_established: List[str] = []

    # Timeline
    story_date: str = ""  # When this happens in story time
    time_span: str = ""  # How long the chapter covers

    # Status
    review: str = ""
    revision_notes: str = ""
    word_count: int = 0
    draft_number: int = 1

    def get_scene(self, scene_number: int) -> Optional[SceneCodex]:
        """Get a specific scene from this chapter"""
        for scene in self.scenes:
            if scene.scene_number == scene_number:
                return scene
        return None


# =============================================================================
# MASTER CODEX
# =============================================================================

class MasterCodex(BaseModel):
    """
    The complete codex for a project, containing all enhanced tracking data.
    This supplements (not replaces) the ProjectKnowledgeBase.
    """
    project_name: str
    version: str = "1.0.0"
    last_updated: str = ""

    # Characters
    characters: Dict[str, CharacterCodex] = {}

    # Chapters & Scenes
    chapters: Dict[int, ChapterCodex] = {}

    # Global Tracking
    callbacks: Dict[str, Callback] = {}  # id -> Callback
    facts: Dict[str, FactEstablished] = {}  # id -> Fact
    memories: Dict[str, Memory] = {}  # id -> Memory (global registry)

    # Themes & Motifs
    global_themes: List[str] = []
    recurring_symbols: Dict[str, str] = {}  # symbol -> meaning
    recurring_motifs: List[str] = []

    # Timeline
    story_timeline: Dict[str, str] = {}  # date/event -> description

    # Quick Access
    character_names: List[str] = []  # All character names for quick lookup
    location_registry: Dict[str, str] = {}  # location_name -> description
    item_registry: Dict[str, str] = {}  # item_name -> description/significance

    def add_character(self, character: CharacterCodex):
        """Add or update a character in the codex"""
        self.characters[character.name] = character
        if character.name not in self.character_names:
            self.character_names.append(character.name)

    def get_character(self, name: str) -> Optional[CharacterCodex]:
        """Get a character by name"""
        return self.characters.get(name)

    def add_chapter(self, chapter: ChapterCodex):
        """Add or update a chapter in the codex"""
        self.chapters[chapter.chapter_number] = chapter

    def get_chapter(self, chapter_number: int) -> Optional[ChapterCodex]:
        """Get a chapter by number"""
        return self.chapters.get(chapter_number)

    def add_callback(self, callback: Callback):
        """Register a narrative callback"""
        if not callback.id:
            callback.id = f"cb_{callback.setup_chapter}_{len(self.callbacks)}"
        self.callbacks[callback.id] = callback

    def get_pending_callbacks(self) -> List[Callback]:
        """Get all callbacks that haven't been paid off"""
        return [cb for cb in self.callbacks.values()
                if cb.status in [CallbackStatus.PLANTED, CallbackStatus.REFERENCED]]

    def add_fact(self, fact: FactEstablished):
        """Register an established fact"""
        if not fact.id:
            fact.id = f"fact_{fact.chapter_established}_{len(self.facts)}"
        self.facts[fact.id] = fact

    def get_facts_before_chapter(self, chapter: int) -> List[FactEstablished]:
        """Get all facts established before or at a chapter"""
        return [f for f in self.facts.values()
                if f.chapter_established <= chapter]

    def get_character_state_at_chapter(self, char_name: str, chapter: int) -> Dict[str, Any]:
        """
        Get the state of a character at a specific chapter.
        Useful for context assembly before writing.
        """
        char = self.get_character(char_name)
        if not char:
            return {}

        return {
            "name": char.name,
            "current_emotions": char.get_emotions_at_chapter(chapter),
            "relevant_memories": char.get_relevant_memories(chapter),
            "relationships": {k: v.dict() for k, v in char.relationships.items()},
            "arc_milestones": [m for m in char.arc_milestones if m.chapter <= chapter],
            "is_alive": char.is_alive if chapter < (char.death_chapter or 999) else False,
            "location": char.current_location,
            "inventory": char.inventory,
        }

    def get_scene_context(self, chapter: int, scene: int) -> Dict[str, Any]:
        """
        Assemble full context for a scene.
        This is what gets passed to the chapter writer.
        """
        ch = self.get_chapter(chapter)
        if not ch:
            return {}

        sc = ch.get_scene(scene)
        if not sc:
            return {}

        # Get character states
        char_states = {}
        for char_name in sc.characters:
            char_states[char_name] = self.get_character_state_at_chapter(char_name, chapter)

        # Get pending callbacks
        pending_callbacks = [cb for cb in self.get_pending_callbacks()
                           if cb.setup_chapter < chapter]

        # Get relevant facts
        relevant_facts = self.get_facts_before_chapter(chapter)

        return {
            "scene": sc.dict(),
            "chapter_context": {
                "chapter_number": ch.chapter_number,
                "title": ch.title,
                "act": ch.act,
                "primary_theme": ch.primary_theme,
            },
            "character_states": char_states,
            "pending_callbacks": [cb.dict() for cb in pending_callbacks],
            "established_facts": [f.dict() for f in relevant_facts],
            "global_themes": self.global_themes,
            "symbols": self.recurring_symbols,
        }

    def to_json(self) -> str:
        """Serialize codex to JSON"""
        self.last_updated = datetime.now().isoformat()
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "MasterCodex":
        """Deserialize codex from JSON"""
        return cls.model_validate_json(json_str)

    def save_to_file(self, file_path: str):
        """Save codex to file"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> Optional["MasterCodex"]:
        """Load codex from file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return cls.from_json(f.read())
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading codex: {e}")
            return None


# =============================================================================
# MIGRATION UTILITIES
# =============================================================================

def migrate_character_to_codex(old_char: Dict[str, Any]) -> CharacterCodex:
    """
    Migrate a character from the old format to the enhanced CharacterCodex.
    Preserves all existing data while adding new structure.
    """
    return CharacterCodex(
        name=old_char.get("name", "Unknown"),
        age_at_story_start=old_char.get("age", ""),
        physical_description=old_char.get("physical_description", ""),
        personality_traits=old_char.get("personality_traits", ""),
        background=old_char.get("background", ""),
        motivations=old_char.get("motivations", ""),
        role=old_char.get("role", ""),
        internal_conflicts=old_char.get("internal_conflicts", ""),
        external_conflicts=old_char.get("external_conflicts", ""),
        character_arc=old_char.get("character_arc", ""),
        # New fields start empty, to be filled in
    )


def migrate_scene_to_codex(chapter: int, old_scene: Dict[str, Any]) -> SceneCodex:
    """
    Migrate a scene from the old format to the enhanced SceneCodex.
    """
    return SceneCodex(
        scene_id=f"ch{chapter}_sc{old_scene.get('scene_number', 0)}",
        chapter=chapter,
        scene_number=old_scene.get("scene_number", 0),
        summary=old_scene.get("summary", ""),
        characters=old_scene.get("characters", []),
        setting=old_scene.get("setting", ""),
        goal=old_scene.get("goal", ""),
        emotional_beat=old_scene.get("emotional_beat", ""),
        location=old_scene.get("setting", ""),  # Use setting as initial location
    )
