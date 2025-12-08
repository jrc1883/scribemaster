# src/libriscribe/utils/book_analyzer.py
"""
Book Analyzer - Comprehensive analysis of a book project

Generates fact sheets, identifies gaps, detects incongruencies,
and provides PopKit-style "what's next" recommendations.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from ..codex import MasterCodex, CallbackStatus


class GapSeverity(str, Enum):
    CRITICAL = "critical"  # Must fix before continuing
    HIGH = "high"  # Should fix soon
    MEDIUM = "medium"  # Worth addressing
    LOW = "low"  # Nice to have
    INFO = "info"  # Just informational


@dataclass
class Gap:
    """A gap or issue identified in the narrative"""
    category: str  # character, plot, world, continuity, etc.
    severity: GapSeverity
    description: str
    location: str  # Where in the story this applies
    suggestion: str  # How to fix it
    related_items: List[str] = field(default_factory=list)


@dataclass
class Opportunity:
    """A narrative opportunity for future payoff"""
    category: str
    description: str
    planted_in: str  # Where it was set up
    potential_payoff: str  # Ideas for payoff
    books_ahead: int = 1  # How many books until payoff (1 = this book)


@dataclass
class NextAction:
    """A recommended next action, PopKit-style"""
    priority: int  # 1-5, 1 being highest
    action: str
    reason: str
    command: str  # The command to run
    category: str  # writing, editing, planning, codex


@dataclass
class BookAnalysis:
    """Complete analysis of a book project"""
    project_name: str

    # Status
    chapters_written: int
    chapters_planned: int
    completion_percent: float

    # Characters
    character_count: int
    characters_with_arcs: List[str]
    characters_underdeveloped: List[str]

    # Callbacks
    callbacks_planted: int
    callbacks_paid_off: int
    callbacks_pending: List[Dict[str, Any]]

    # Gaps
    gaps: List[Gap]

    # Opportunities
    opportunities: List[Opportunity]

    # Next Actions
    next_actions: List[NextAction]

    # Themes & Symbols
    themes: List[str]
    symbols: Dict[str, str]

    # Quick Stats
    scene_count: int
    character_appearances: Dict[str, int]


class BookAnalyzer:
    """Analyzes a book project for gaps, opportunities, and next actions"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.codex: Optional[MasterCodex] = None
        self.project_data: Optional[Dict] = None
        self.chapters_content: Dict[int, str] = {}
        self.outline_content: str = ""

    def load_data(self) -> bool:
        """Load all project data"""
        # Load codex
        codex_path = self.project_dir / "codex.json"
        if codex_path.exists():
            self.codex = MasterCodex.load_from_file(str(codex_path))

        # Load project data
        project_data_path = self.project_dir / "project_data.json"
        if project_data_path.exists():
            with open(project_data_path, "r", encoding="utf-8") as f:
                self.project_data = json.load(f)

        # Load outline
        outline_path = self.project_dir / "outline.md"
        if outline_path.exists():
            with open(outline_path, "r", encoding="utf-8") as f:
                self.outline_content = f.read()

        # Load chapter content
        for chapter_file in self.project_dir.glob("chapter_*.md"):
            try:
                # Extract chapter number
                name = chapter_file.stem
                if "_revised" in name:
                    num = int(name.replace("chapter_", "").replace("_revised", ""))
                else:
                    num = int(name.replace("chapter_", ""))

                with open(chapter_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Prefer revised versions
                    if "_revised" in str(chapter_file) or num not in self.chapters_content:
                        self.chapters_content[num] = content
            except (ValueError, IOError):
                continue

        return self.codex is not None or self.project_data is not None

    def analyze(self) -> BookAnalysis:
        """Run full analysis and return results"""
        if not self.load_data():
            raise ValueError("Could not load project data")

        # Basic stats
        chapters_written = len(self.chapters_content)
        chapters_planned = self._get_planned_chapters()
        completion = (chapters_written / chapters_planned * 100) if chapters_planned > 0 else 0

        # Character analysis
        char_analysis = self._analyze_characters()

        # Callback analysis
        callback_analysis = self._analyze_callbacks()

        # Gap detection
        gaps = self._detect_gaps()

        # Opportunity identification
        opportunities = self._identify_opportunities()

        # Next actions
        next_actions = self._generate_next_actions(gaps, callback_analysis, completion)

        # Scene count
        scene_count = sum(
            len(ch.scenes) for ch in (self.codex.chapters.values() if self.codex else [])
        )

        # Character appearances
        char_appearances = self._count_character_appearances()

        return BookAnalysis(
            project_name=self.project_dir.name,
            chapters_written=chapters_written,
            chapters_planned=chapters_planned,
            completion_percent=round(completion, 1),
            character_count=len(char_analysis["all"]),
            characters_with_arcs=char_analysis["with_arcs"],
            characters_underdeveloped=char_analysis["underdeveloped"],
            callbacks_planted=callback_analysis["planted"],
            callbacks_paid_off=callback_analysis["paid_off"],
            callbacks_pending=callback_analysis["pending"],
            gaps=gaps,
            opportunities=opportunities,
            next_actions=next_actions,
            themes=self.codex.global_themes if self.codex else [],
            symbols=self.codex.recurring_symbols if self.codex else {},
            scene_count=scene_count,
            character_appearances=char_appearances,
        )

    def _get_planned_chapters(self) -> int:
        """Get the number of planned chapters"""
        if self.project_data:
            num = self.project_data.get("num_chapters", 24)
            if isinstance(num, tuple):
                return num[1]  # Upper bound
            return num
        return 24  # Default

    def _analyze_characters(self) -> Dict[str, List[str]]:
        """Analyze character development status"""
        result = {
            "all": [],
            "with_arcs": [],
            "underdeveloped": [],
        }

        if not self.codex:
            return result

        for name, char in self.codex.characters.items():
            result["all"].append(name)

            # Check if well-developed
            has_arc = bool(char.character_arc)
            has_psychology = bool(char.psychology.fears or char.psychology.desires)
            has_relationships = bool(char.relationships)
            appears_enough = len(char.scenes_appeared) >= 3

            if has_arc and (has_psychology or appears_enough):
                result["with_arcs"].append(name)
            else:
                result["underdeveloped"].append(name)

        return result

    def _analyze_callbacks(self) -> Dict[str, Any]:
        """Analyze callback/foreshadowing status"""
        result = {
            "planted": 0,
            "paid_off": 0,
            "pending": [],
        }

        if not self.codex:
            return result

        for cb_id, cb in self.codex.callbacks.items():
            status = cb.status if isinstance(cb.status, str) else cb.status.value

            if status in ["planted", "referenced"]:
                result["planted"] += 1
                result["pending"].append({
                    "name": cb.name,
                    "setup_chapter": cb.setup_chapter,
                    "importance": cb.importance if isinstance(cb.importance, str) else cb.importance,
                    "description": cb.setup_description,
                })
            elif status == "paid_off":
                result["paid_off"] += 1

        return result

    def _detect_gaps(self) -> List[Gap]:
        """Detect gaps and potential issues in the narrative"""
        gaps = []

        if not self.codex:
            gaps.append(Gap(
                category="setup",
                severity=GapSeverity.HIGH,
                description="No codex found - run codex-migrate first",
                location="Project setup",
                suggestion="Run: scribemaster codex-migrate -p \"Your Project\"",
            ))
            return gaps

        # Character gaps
        for name, char in self.codex.characters.items():
            # No physical description
            if not char.physical_description:
                gaps.append(Gap(
                    category="character",
                    severity=GapSeverity.MEDIUM,
                    description=f"{name} has no physical description",
                    location=f"Character: {name}",
                    suggestion="Add distinguishing physical features for reader visualization",
                ))

            # No relationships defined
            if not char.relationships and len(char.scenes_appeared) > 5:
                gaps.append(Gap(
                    category="character",
                    severity=GapSeverity.HIGH,
                    description=f"{name} appears often but has no defined relationships",
                    location=f"Character: {name}",
                    suggestion="Define relationships with other main characters",
                    related_items=[c for c in self.codex.character_names if c != name][:3],
                ))

            # Character appears in outline but never in scenes
            if len(char.scenes_appeared) == 0 and char.character_arc:
                gaps.append(Gap(
                    category="character",
                    severity=GapSeverity.INFO,
                    description=f"{name} has arc defined but hasn't appeared in scenes yet",
                    location=f"Character: {name}",
                    suggestion="Ensure they're introduced appropriately per their arc",
                ))

        # Callback gaps - critical callbacks that are overdue
        chapters_written = len(self.chapters_content)
        for cb_id, cb in self.codex.callbacks.items():
            status = cb.status if isinstance(cb.status, str) else cb.status.value
            importance = cb.importance if isinstance(cb.importance, str) else cb.importance

            if status in ["planted", "referenced"]:
                chapters_since = chapters_written - cb.setup_chapter

                # Critical callbacks should have some movement by midpoint
                if importance == "critical" and chapters_since > 8:
                    gaps.append(Gap(
                        category="plot",
                        severity=GapSeverity.HIGH,
                        description=f"Critical callback '{cb.name}' planted {chapters_since} chapters ago with no payoff",
                        location=f"Chapter {cb.setup_chapter}",
                        suggestion="Reference or begin payoff of this element soon",
                        related_items=[cb.setup_description],
                    ))

        # Scene continuity gaps
        for ch_num, chapter in self.codex.chapters.items():
            for scene in chapter.scenes:
                # Check for empty emotional beats
                if not scene.emotional_beat:
                    gaps.append(Gap(
                        category="continuity",
                        severity=GapSeverity.LOW,
                        description=f"Ch{ch_num} Scene {scene.scene_number} missing emotional beat",
                        location=f"Chapter {ch_num}, Scene {scene.scene_number}",
                        suggestion="Define the emotional purpose of this scene",
                    ))

        return gaps

    def _identify_opportunities(self) -> List[Opportunity]:
        """Identify narrative opportunities for future payoff"""
        opportunities = []

        if not self.codex:
            return opportunities

        # Characters with unrealized potential
        for name, char in self.codex.characters.items():
            # Characters with secrets or unresolved internal conflicts
            if char.psychology.secrets:
                opportunities.append(Opportunity(
                    category="character",
                    description=f"{name}'s secrets could be revealed later",
                    planted_in="Character backstory",
                    potential_payoff="Dramatic revelation scene, trust-breaking moment",
                    books_ahead=1,
                ))

            # Redemption arcs
            arc_type = char.arc_type if isinstance(char.arc_type, str) else char.arc_type.value
            if arc_type == "redemption":
                opportunities.append(Opportunity(
                    category="character",
                    description=f"{name}'s redemption arc could have long-term ripples",
                    planted_in=f"Character setup for {name}",
                    potential_payoff="Moment of sacrifice, teaching the next generation",
                    books_ahead=2,
                ))

        # Symbols that could recur
        for symbol, meaning in self.codex.recurring_symbols.items():
            opportunities.append(Opportunity(
                category="symbol",
                description=f"'{symbol}' symbol can recur with deepened meaning",
                planted_in="Book 1 symbolism",
                potential_payoff=f"Transform meaning: {meaning} → evolved significance",
                books_ahead=3,
            ))

        # Worldbuilding elements
        if self.codex.location_registry:
            for location, desc in list(self.codex.location_registry.items())[:3]:
                opportunities.append(Opportunity(
                    category="world",
                    description=f"Location '{location}' could become significant later",
                    planted_in="Worldbuilding",
                    potential_payoff="Return to this place with new meaning/stakes",
                    books_ahead=2,
                ))

        return opportunities

    def _generate_next_actions(self, gaps: List[Gap], callbacks: Dict,
                                completion: float) -> List[NextAction]:
        """Generate PopKit-style next action recommendations"""
        actions = []
        priority = 1

        # Critical gaps first
        critical_gaps = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
        for gap in critical_gaps[:2]:
            actions.append(NextAction(
                priority=priority,
                action=f"Fix: {gap.description}",
                reason=f"Critical issue in {gap.category}",
                command=gap.suggestion,
                category="fix",
            ))
            priority += 1

        # Check completion status
        if completion < 100:
            chapters_remaining = self._get_planned_chapters() - len(self.chapters_content)
            next_chapter = max(self.chapters_content.keys()) + 1 if self.chapters_content else 1

            actions.append(NextAction(
                priority=priority,
                action=f"Write Chapter {next_chapter}",
                reason=f"{chapters_remaining} chapters remaining ({completion:.0f}% complete)",
                command=f"scribemaster write --chapter-number {next_chapter}",
                category="writing",
            ))
            priority += 1

        # Pending callbacks that need attention
        pending_critical = [c for c in callbacks.get("pending", [])
                          if c.get("importance") == "critical"]
        if pending_critical:
            cb = pending_critical[0]
            actions.append(NextAction(
                priority=priority,
                action=f"Address callback: {cb['name']}",
                reason=f"Critical foreshadowing from Ch{cb['setup_chapter']} needs payoff",
                command=f"scribemaster codex-show callbacks",
                category="planning",
            ))
            priority += 1

        # High-priority gaps
        high_gaps = [g for g in gaps if g.severity == GapSeverity.HIGH][:2]
        for gap in high_gaps:
            actions.append(NextAction(
                priority=priority,
                action=gap.suggestion,
                reason=gap.description,
                command="# Manual edit in codex",
                category="codex",
            ))
            priority += 1

        # Codex enhancement
        if self.codex:
            underdeveloped = [n for n, c in self.codex.characters.items()
                            if not c.relationships]
            if underdeveloped:
                actions.append(NextAction(
                    priority=priority,
                    action=f"Define relationships for {underdeveloped[0]}",
                    reason="Characters need relationship mapping for continuity",
                    command=f"# Edit codex.json - add relationships for {underdeveloped[0]}",
                    category="codex",
                ))
                priority += 1

        # If book is complete, suggest review
        if completion >= 100:
            actions.append(NextAction(
                priority=1,
                action="Run consistency review",
                reason="Book draft complete - check for incongruencies",
                command="scribemaster codex-show callbacks",
                category="editing",
            ))

        return sorted(actions, key=lambda a: a.priority)[:7]  # Top 7 actions

    def _count_character_appearances(self) -> Dict[str, int]:
        """Count how often each character appears"""
        counts = defaultdict(int)

        if self.codex:
            for name, char in self.codex.characters.items():
                counts[name] = len(char.scenes_appeared)

        return dict(counts)

    def generate_fact_sheet(self) -> str:
        """Generate a printable fact sheet for the book"""
        analysis = self.analyze()

        lines = []
        lines.append("=" * 70)
        lines.append(f"  FACT SHEET: {analysis.project_name}")
        lines.append("=" * 70)
        lines.append("")

        # Progress
        lines.append("## PROGRESS")
        lines.append(f"  Chapters: {analysis.chapters_written}/{analysis.chapters_planned} ({analysis.completion_percent}%)")
        lines.append(f"  Scenes: {analysis.scene_count}")
        lines.append("")

        # Characters
        lines.append("## CHARACTERS ({})".format(analysis.character_count))
        for name, count in sorted(analysis.character_appearances.items(),
                                   key=lambda x: -x[1]):
            status = "developed" if name in analysis.characters_with_arcs else "needs work"
            lines.append(f"  - {name}: {count} scenes [{status}]")
        lines.append("")

        # Callbacks / Foreshadowing
        lines.append("## CALLBACKS & FORESHADOWING")
        lines.append(f"  Planted: {analysis.callbacks_planted}")
        lines.append(f"  Paid Off: {analysis.callbacks_paid_off}")
        if analysis.callbacks_pending:
            lines.append("  Pending:")
            for cb in analysis.callbacks_pending:
                lines.append(f"    [{cb['importance'].upper()}] {cb['name']} (Ch{cb['setup_chapter']})")
                lines.append(f"      {cb['description'][:60]}...")
        lines.append("")

        # Themes & Symbols
        if analysis.themes:
            lines.append("## THEMES")
            for theme in analysis.themes:
                lines.append(f"  - {theme}")
            lines.append("")

        if analysis.symbols:
            lines.append("## SYMBOLS")
            for symbol, meaning in analysis.symbols.items():
                lines.append(f"  {symbol}: {meaning[:50]}...")
            lines.append("")

        # Gaps
        if analysis.gaps:
            lines.append("## GAPS & ISSUES")
            by_severity = defaultdict(list)
            for gap in analysis.gaps:
                sev = gap.severity.value if hasattr(gap.severity, 'value') else gap.severity
                by_severity[sev].append(gap)

            for severity in ["critical", "high", "medium", "low", "info"]:
                if severity in by_severity:
                    lines.append(f"  [{severity.upper()}]")
                    for gap in by_severity[severity][:3]:  # Top 3 per severity
                        lines.append(f"    - {gap.description}")
                        lines.append(f"      Fix: {gap.suggestion}")
            lines.append("")

        # Opportunities
        if analysis.opportunities:
            lines.append("## FUTURE OPPORTUNITIES (for later books)")
            for opp in analysis.opportunities[:5]:
                lines.append(f"  [{opp.category}] {opp.description}")
                lines.append(f"    Payoff idea: {opp.potential_payoff}")
            lines.append("")

        # Next Actions
        lines.append("## WHAT'S NEXT (prioritized)")
        for action in analysis.next_actions:
            lines.append(f"  {action.priority}. [{action.category.upper()}] {action.action}")
            lines.append(f"     Why: {action.reason}")
            if not action.command.startswith("#"):
                lines.append(f"     Run: {action.command}")
        lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)


def analyze_book(project_path: str) -> BookAnalysis:
    """Convenience function to analyze a book"""
    analyzer = BookAnalyzer(Path(project_path))
    return analyzer.analyze()


def print_fact_sheet(project_path: str) -> str:
    """Generate and return the fact sheet"""
    analyzer = BookAnalyzer(Path(project_path))
    return analyzer.generate_fact_sheet()
