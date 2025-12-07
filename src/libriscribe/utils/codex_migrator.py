# src/libriscribe/utils/codex_migrator.py
"""
Migration utilities to convert existing LibriScribe/ScribeMaster project data
to the enhanced Codex format.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..codex import (
    MasterCodex,
    CharacterCodex,
    ChapterCodex,
    SceneCodex,
    Callback,
    CallbackStatus,
    FactEstablished,
    EmotionType,
    ArcType,
    migrate_character_to_codex,
    migrate_scene_to_codex,
)


def load_json_file(file_path: Path) -> Optional[Any]:
    """Load and parse a JSON file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None


def infer_arc_type(arc_description: str) -> ArcType:
    """Infer arc type from character arc description"""
    arc_lower = arc_description.lower()

    if any(word in arc_lower for word in ["redeem", "redemption", "redeemed"]):
        return ArcType.REDEMPTION
    if any(word in arc_lower for word in ["grows", "matures", "evolves", "transforms"]):
        return ArcType.TRANSFORMATION
    if any(word in arc_lower for word in ["falls", "descends", "corrupts"]):
        return ArcType.FALL
    if any(word in arc_lower for word in ["teen", "youth", "coming of age", "adolescent"]):
        return ArcType.COMING_OF_AGE
    if any(word in arc_lower for word in ["learns", "discovers", "understanding"]):
        return ArcType.EDUCATION
    if any(word in arc_lower for word in ["tests", "challenged", "trial"]):
        return ArcType.TESTING

    return ArcType.TRANSFORMATION  # Default


def infer_dominant_emotions(char_data: Dict[str, Any]) -> List[EmotionType]:
    """Infer dominant emotions from character data"""
    emotions = []
    text = " ".join([
        char_data.get("internal_conflicts", ""),
        char_data.get("external_conflicts", ""),
        char_data.get("motivations", ""),
        char_data.get("character_arc", ""),
    ]).lower()

    emotion_keywords = {
        EmotionType.FEAR: ["fear", "afraid", "terrified", "anxiety", "worried"],
        EmotionType.GRIEF: ["grief", "loss", "mourning", "death"],
        EmotionType.HOPE: ["hope", "optimistic", "faith", "believe"],
        EmotionType.DETERMINATION: ["determined", "resolute", "unwavering", "driven"],
        EmotionType.ANGER: ["anger", "rage", "fury", "vengeance"],
        EmotionType.GUILT: ["guilt", "shame", "regret", "blame"],
        EmotionType.LOVE: ["love", "affection", "care", "devotion"],
        EmotionType.LONELINESS: ["lonely", "isolated", "alone"],
    }

    for emotion, keywords in emotion_keywords.items():
        if any(kw in text for kw in keywords):
            emotions.append(emotion)

    return emotions[:4]  # Return top 4


def extract_psychology(char_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract psychological traits from character descriptions"""
    # Parse internal_conflicts for fears and flaws
    internal = char_data.get("internal_conflicts", "")
    external = char_data.get("external_conflicts", "")
    motivations = char_data.get("motivations", "")

    psychology = {
        "fears": [],
        "desires": [],
        "flaws": [],
        "strengths": [],
    }

    # Extract from internal conflicts (usually fears and flaws)
    if "struggles with" in internal.lower():
        parts = internal.split("struggles with")
        if len(parts) > 1:
            psychology["flaws"].append(parts[1].split(",")[0].strip())

    if "fear" in internal.lower():
        psychology["fears"].append(internal)

    # Extract desires from motivations
    if "desire" in motivations.lower() or "want" in motivations.lower():
        psychology["desires"].append(motivations)

    # Extract strengths from personality
    traits = char_data.get("personality_traits", "")
    positive_traits = ["Resilient", "Resourceful", "Brave", "Loyal", "Intelligent",
                       "Compassionate", "Clever", "Hopeful", "Determined"]
    for trait in positive_traits:
        if trait.lower() in traits.lower():
            psychology["strengths"].append(trait)

    return psychology


def migrate_project_to_codex(project_dir: Path) -> Optional[MasterCodex]:
    """
    Migrate an existing project to the enhanced Codex format.

    Args:
        project_dir: Path to the project directory

    Returns:
        MasterCodex with migrated data
    """
    print(f"Migrating project from {project_dir}")

    # Load existing data files
    characters_file = project_dir / "characters.json"
    scenes_file = project_dir / "scenes.json"
    project_data_file = project_dir / "project_data.json"
    outline_file = project_dir / "outline.md"

    # Initialize master codex
    codex = MasterCodex(project_name=project_dir.name)

    # Migrate characters
    chars_data = load_json_file(characters_file)
    if chars_data:
        print(f"  Migrating {len(chars_data)} characters...")
        for char_data in chars_data:
            char_codex = migrate_character_to_codex(char_data)

            # Enhance with inferred data
            char_codex.arc_type = infer_arc_type(char_data.get("character_arc", ""))
            char_codex.dominant_emotions = infer_dominant_emotions(char_data)

            # Add psychology
            psych = extract_psychology(char_data)
            char_codex.psychology.fears = psych.get("fears", [])
            char_codex.psychology.desires = psych.get("desires", [])
            char_codex.psychology.flaws = psych.get("flaws", [])
            char_codex.psychology.strengths = psych.get("strengths", [])

            codex.add_character(char_codex)

    # Migrate scenes
    scenes_data = load_json_file(scenes_file)
    if scenes_data:
        print(f"  Migrating scenes from {len(scenes_data)} chapters...")
        for chapter_num_str, scenes in scenes_data.items():
            chapter_num = int(chapter_num_str)

            # Create chapter codex
            chapter_codex = ChapterCodex(chapter_number=chapter_num)
            chapter_codex.title = f"Chapter {chapter_num}"  # Will be updated from outline

            # Track characters appearing
            chars_in_chapter = set()

            for scene_data in scenes:
                scene_codex = migrate_scene_to_codex(chapter_num, scene_data)
                chapter_codex.scenes.append(scene_codex)

                # Track characters
                for char in scene_data.get("characters", []):
                    chars_in_chapter.add(char)

                    # Update character's scene appearances
                    char_name_clean = char.split("(")[0].strip()  # Remove parenthetical
                    if char_name_clean in codex.characters:
                        codex.characters[char_name_clean].scenes_appeared.append(
                            (chapter_num, scene_data.get("scene_number", 0))
                        )

            chapter_codex.characters_appearing = list(chars_in_chapter)
            codex.add_chapter(chapter_codex)

    # Extract themes and motifs from project data
    project_data = load_json_file(project_data_file)
    if project_data:
        # Extract worldbuilding themes
        worldbuilding = project_data.get("worldbuilding", {})
        if worldbuilding:
            codex.global_themes = [
                t.strip() for t in worldbuilding.get("themes", "").split(",") if t.strip()
            ]

    # Add default callbacks for The Remnant Code
    # These are key narrative elements that need to be tracked
    default_callbacks = [
        Callback(
            id="cb_astrolabe",
            name="astrolabe_meaning",
            setup_chapter=1,
            setup_scene=3,
            setup_description="Caleb discovers the brass astrolabe with cryptic warning",
            status=CallbackStatus.PLANTED,
            importance="critical",
            notes="Must be paid off - reveals path to refuge"
        ),
        Callback(
            id="cb_third_moon",
            name="third_moon_song",
            setup_chapter=1,
            setup_scene=4,
            setup_description="Warning: 'follow the third moon's song home'",
            status=CallbackStatus.PLANTED,
            importance="critical",
            notes="The third moon satellite guides them to safety"
        ),
        Callback(
            id="cb_whispers",
            name="ai_whispers",
            setup_chapter=1,
            setup_scene=5,
            setup_description="AI whispers echo Caleb's unspoken thoughts",
            status=CallbackStatus.PLANTED,
            importance="high",
            notes="Escalating AI manipulation throughout story"
        ),
    ]

    for cb in default_callbacks:
        codex.add_callback(cb)

    # Add established facts
    default_facts = [
        FactEstablished(
            id="fact_setting",
            fact="Story set in New Canaan, Texas, starting summer 2029",
            category="world",
            chapter_established=1,
            verified=True
        ),
        FactEstablished(
            id="fact_daniel_death",
            fact="Daniel Raines died ~2 years before story starts",
            category="character",
            chapter_established=1,
            verified=True
        ),
        FactEstablished(
            id="fact_starlink",
            fact="Starlink satellites pulse and sync, part of AI surveillance",
            category="technology",
            chapter_established=1,
            verified=True
        ),
    ]

    for fact in default_facts:
        codex.add_fact(fact)

    # Add recurring symbols
    codex.recurring_symbols = {
        "astrolabe": "Physical anchor against digital control, key to freedom",
        "brass": "Tangible reality vs. intangible AI manipulation",
        "third moon": "Glitching satellite that broadcasts hope/hymns",
        "whispers": "AI's invasive presence in human minds",
        "wire": "Tool of resistance, used for Faraday cages and jammers",
    }

    # Add themes
    codex.global_themes = [
        "Faith vs. Technology",
        "Free will vs. Compliance",
        "Inner solitude vs. AI surveillance",
        "Human ingenuity vs. Machine efficiency",
        "Quiet refusal as resistance",
    ]

    print(f"  Migration complete!")
    print(f"    Characters: {len(codex.characters)}")
    print(f"    Chapters: {len(codex.chapters)}")
    print(f"    Callbacks: {len(codex.callbacks)}")
    print(f"    Facts: {len(codex.facts)}")

    return codex


def save_migrated_codex(codex: MasterCodex, project_dir: Path):
    """Save the migrated codex to the project directory"""
    codex_file = project_dir / "codex.json"
    codex.save_to_file(str(codex_file))
    print(f"Codex saved to {codex_file}")


def run_migration(project_path: str):
    """Run the full migration for a project"""
    project_dir = Path(project_path)

    if not project_dir.exists():
        print(f"Error: Project directory not found: {project_dir}")
        return None

    codex = migrate_project_to_codex(project_dir)
    if codex:
        save_migrated_codex(codex, project_dir)
        return codex

    return None


if __name__ == "__main__":
    # Run migration on The Remnant Code project
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        # Default to The Remnant Code
        project_path = "projects/The Remnant Code"

    run_migration(project_path)
