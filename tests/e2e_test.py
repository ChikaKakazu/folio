#!/usr/bin/env python3
"""
Folio E2E Test Suite

Tests the complete workflow of the Folio novel orchestration system.
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime


# Base paths
BASE_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
CURRENT_DIR = WORKSPACE_DIR / "current"
PATHS_DIR = WORKSPACE_DIR / "paths"
OUTPUT_DIR = BASE_DIR / "output"
PROMPTS_DIR = BASE_DIR / "prompts"
COMMANDS_DIR = BASE_DIR / ".claude" / "commands"


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, name: str):
        self.passed += 1
        print(f"  ✓ {name}")

    def fail(self, name: str, reason: str):
        self.failed += 1
        self.errors.append(f"{name}: {reason}")
        print(f"  ✗ {name}")
        print(f"    └─ {reason}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'━' * 50}")
        print(f"Results: {self.passed}/{total} passed")
        if self.errors:
            print(f"\nFailed tests:")
            for err in self.errors:
                print(f"  • {err}")
        return self.failed == 0


def test_directory_structure(result: TestResult):
    """Test that all required directories exist."""
    print("\n[1] Directory Structure")

    required_dirs = [
        WORKSPACE_DIR,
        CURRENT_DIR,
        PATHS_DIR,
        OUTPUT_DIR,
        PROMPTS_DIR,
        PROMPTS_DIR / "crew",
        PROMPTS_DIR / "templates",
        COMMANDS_DIR,
    ]

    for dir_path in required_dirs:
        if dir_path.exists() and dir_path.is_dir():
            result.ok(f"Directory exists: {dir_path.relative_to(BASE_DIR)}")
        else:
            result.fail(f"Directory missing: {dir_path.relative_to(BASE_DIR)}", "Not found")


def test_prompt_files(result: TestResult):
    """Test that all required prompt files exist and have content."""
    print("\n[2] Prompt Files")

    required_files = [
        ("editor.md", PROMPTS_DIR / "editor.md"),
        ("plotter.md", PROMPTS_DIR / "crew" / "plotter.md"),
        ("persona.md", PROMPTS_DIR / "crew" / "persona.md"),
        ("stylist.md", PROMPTS_DIR / "crew" / "stylist.md"),
        ("pacer.md", PROMPTS_DIR / "crew" / "pacer.md"),
        ("character-sheet.md", PROMPTS_DIR / "templates" / "character-sheet.md"),
        ("character-export.md", PROMPTS_DIR / "templates" / "character-export.md"),
    ]

    for name, file_path in required_files:
        if file_path.exists():
            content = file_path.read_text()
            if len(content) > 100:
                result.ok(f"Prompt file: {name} ({len(content)} chars)")
            else:
                result.fail(f"Prompt file: {name}", "File too small (< 100 chars)")
        else:
            result.fail(f"Prompt file: {name}", "Not found")


def test_command_files(result: TestResult):
    """Test that all command files exist."""
    print("\n[3] Command Files")

    required_commands = [
        "folio.md",
        "export.md",
        "status.md",
        "characters.md",
        "foreshadowing.md",
        "chapter-status.md",
    ]

    for cmd in required_commands:
        cmd_path = COMMANDS_DIR / cmd
        if cmd_path.exists():
            result.ok(f"Command: /{cmd.replace('.md', '')}")
        else:
            result.fail(f"Command: /{cmd.replace('.md', '')}", f"{cmd} not found")


def test_editor_content(result: TestResult):
    """Test editor.md contains required sections."""
    print("\n[4] Editor Content (v2 Features)")

    editor_path = PROMPTS_DIR / "editor.md"
    if not editor_path.exists():
        result.fail("Editor file", "editor.md not found")
        return

    content = editor_path.read_text()

    required_sections = [
        ("Phase 0: Intake", "Phase 0"),
        ("Phase 1: Paths", "Phase 1"),
        ("Phase 2: Select", "Phase 2"),
        ("Phase 3: Design", "Phase 3"),
        ("Phase 4: Loop", "Phase 4"),
        ("Episode Gate", "Episode Gate"),
        ("Chapter Gate", "Chapter Gate"),
        ("Foreshadowing", "foreshadowing"),
        ("character_confirmation gate", "character_confirmation"),
        ("chapter_outline gate", "chapter_outline"),
        ("chapter_completion gate", "chapter_completion"),
        ("new_character gate", "new_character"),
        ("Scale Settings", "scale"),
    ]

    for name, keyword in required_sections:
        if keyword.lower() in content.lower():
            result.ok(f"Section: {name}")
        else:
            result.fail(f"Section: {name}", f"Keyword '{keyword}' not found")


def test_plotter_content(result: TestResult):
    """Test plotter.md contains required v2 features."""
    print("\n[5] Plotter Content (v2 Features)")

    plotter_path = PROMPTS_DIR / "crew" / "plotter.md"
    if not plotter_path.exists():
        result.fail("Plotter file", "plotter.md not found")
        return

    content = plotter_path.read_text()

    required_features = [
        ("Episode Draft Generation", "Episode Draft"),
        ("Chapter Flow Generation", "Chapter Flow"),
        ("New Character Proposal", "new_character_proposal"),
        ("Episode Hook axis", "episode_hook"),
        ("Web Novel Pacing axis", "web_novel_pacing"),
        ("Foreshadowing detection", "foreshadowing"),
        ("Word count target (2000-4000)", "2,000"),
    ]

    for name, keyword in required_features:
        if keyword in content:
            result.ok(f"Feature: {name}")
        else:
            result.fail(f"Feature: {name}", f"'{keyword}' not found")


def test_pacer_content(result: TestResult):
    """Test pacer.md contains required v2 features."""
    print("\n[6] Pacer Content (v2 Features)")

    pacer_path = PROMPTS_DIR / "crew" / "pacer.md"
    if not pacer_path.exists():
        result.fail("Pacer file", "pacer.md not found")
        return

    content = pacer_path.read_text()

    required_features = [
        ("Episode Hook axis", "episode_hook"),
        ("Web Novel Pacing axis", "web_novel_pacing"),
        ("Episode hook assessment", "episode_hook_assessment"),
        ("Web novel assessment", "web_novel_assessment"),
    ]

    for name, keyword in required_features:
        if keyword in content:
            result.ok(f"Feature: {name}")
        else:
            result.fail(f"Feature: {name}", f"'{keyword}' not found")


def test_persona_content(result: TestResult):
    """Test persona.md contains required v2 features."""
    print("\n[7] Persona Content (v2 Features)")

    persona_path = PROMPTS_DIR / "crew" / "persona.md"
    if not persona_path.exists():
        result.fail("Persona file", "persona.md not found")
        return

    content = persona_path.read_text()

    required_features = [
        ("Character sheet compliance", "character_sheet_compliance"),
        ("New character necessity", "new_character_necessity"),
        ("New character assessment", "new_character_assessment"),
    ]

    for name, keyword in required_features:
        if keyword in content:
            result.ok(f"Feature: {name}")
        else:
            result.fail(f"Feature: {name}", f"'{keyword}' not found")


def test_workspace_initialization(result: TestResult):
    """Test workspace can be initialized correctly."""
    print("\n[8] Workspace Initialization")

    # Clean up test area
    test_dir = CURRENT_DIR / "_test"
    if test_dir.exists():
        shutil.rmtree(test_dir)

    # Create test structure
    try:
        test_dir.mkdir(parents=True)

        # Test state.json creation
        state = {
            "phase": 0,
            "status": "initializing",
            "created_at": datetime.now().isoformat()
        }
        state_file = test_dir / "state.json"
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))
        result.ok("Create state.json")

        # Test idea.json creation
        idea = {
            "title": "テストタイトル",
            "genre": "SF",
            "tone": "serious",
            "scale": "short",
            "core_theme": "テスト用テーマ"
        }
        idea_file = test_dir / "idea.json"
        idea_file.write_text(json.dumps(idea, indent=2, ensure_ascii=False))
        result.ok("Create idea.json")

        # Test progress.json creation
        progress = {
            "phase": 1,
            "awaiting_user": False,
            "current_chapter": None,
            "current_episode": None,
            "message": "Generating paths..."
        }
        progress_file = test_dir / "progress.json"
        progress_file.write_text(json.dumps(progress, indent=2, ensure_ascii=False))
        result.ok("Create progress.json")

        # Test foreshadowing.json creation
        foreshadowing = {
            "version": 1,
            "items": []
        }
        foreshadowing_file = test_dir / "foreshadowing.json"
        foreshadowing_file.write_text(json.dumps(foreshadowing, indent=2, ensure_ascii=False))
        result.ok("Create foreshadowing.json")

        # Test chapter structure
        ch_dir = test_dir / "chapters" / "ch01" / "ep01" / "reviews" / "round-1"
        ch_dir.mkdir(parents=True)
        result.ok("Create chapter/episode structure")

        # Clean up
        shutil.rmtree(test_dir)
        result.ok("Cleanup test directory")

    except Exception as e:
        result.fail("Workspace initialization", str(e))
        if test_dir.exists():
            shutil.rmtree(test_dir)


def test_gate_types_documented(result: TestResult):
    """Test that all gate types are documented in CLAUDE.md."""
    print("\n[9] Gate Types in CLAUDE.md")

    claude_md = BASE_DIR / "CLAUDE.md"
    if not claude_md.exists():
        result.fail("CLAUDE.md", "File not found")
        return

    content = claude_md.read_text()

    gate_types = [
        "path_and_scale",
        "character_confirmation",
        "chapter_outline",
        "chapter_completion",
        "new_character",
    ]

    for gate in gate_types:
        if gate in content:
            result.ok(f"Gate type: {gate}")
        else:
            result.fail(f"Gate type: {gate}", "Not documented in CLAUDE.md")


def test_output_structure(result: TestResult):
    """Test output directory structure."""
    print("\n[10] Output Structure")

    # Check output directories exist or can be created
    output_dirs = [
        OUTPUT_DIR / "characters",
        OUTPUT_DIR / "episodes",
    ]

    for dir_path in output_dirs:
        if dir_path.exists():
            result.ok(f"Output dir exists: {dir_path.name}")
        else:
            try:
                dir_path.mkdir(parents=True)
                result.ok(f"Output dir created: {dir_path.name}")
            except Exception as e:
                result.fail(f"Output dir: {dir_path.name}", str(e))


def main():
    print("=" * 50)
    print("Folio E2E Test Suite")
    print("=" * 50)
    print(f"Base directory: {BASE_DIR}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    result = TestResult()

    # Run all tests
    test_directory_structure(result)
    test_prompt_files(result)
    test_command_files(result)
    test_editor_content(result)
    test_plotter_content(result)
    test_pacer_content(result)
    test_persona_content(result)
    test_workspace_initialization(result)
    test_gate_types_documented(result)
    test_output_structure(result)

    # Print summary
    success = result.summary()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
