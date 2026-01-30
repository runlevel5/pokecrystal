#!/usr/bin/env python3
"""
Check that text lines in assembly files don't exceed the maximum character width.
This helps ensure text fits on the Game Boy screen (20 tiles wide, but typically 18 usable).
"""

import sys
import re
import os
from pathlib import Path

# Maximum characters per line (Game Boy screen is 20 tiles, but borders take 2)
MAX_LINE_LENGTH = 18

# Patterns to match text definitions
# Matches: db "text here"
DB_STRING_PATTERN = re.compile(r'^\s*db\s+"([^"]*)"')

# Characters that map to control codes (don't count towards visible length)
CONTROL_CODES = {
    "<NULL>",
    "<PLAY_G>",
    "<MOBILE>",
    "<CR>",
    "<BSP>",
    "<LF>",
    "<POKE>",
    "<WBR>",
    "<RED>",
    "<GREEN>",
    "<ENEMY>",
    "<MOM>",
    "<PKMN>",
    "<_CONT>",
    "<SCROLL>",
    "<NEXT>",
    "<LINE>",
    "<PARA>",
    "<PLAYER>",
    "<RIVAL>",
    "<CONT>",
    "<……>",
    "<DONE>",
    "<PROMPT>",
    "<TARGET>",
    "<USER>",
    "<PC>",
    "<TM>",
    "<TRAINER>",
    "<ROCKET>",
    "<DEXEND>",
    "<PK>",
    "<MN>",
    "<DOT>",
    "<COLON>",
    "<JP_18>",
    "<NI>",
    "<TTE>",
    "<WO>",
    "<TA!>",
    "<KOUGEKI>",
    "<WA>",
    "<NO>",
    "<ROUTE>",
    "<WATASHI>",
    "<KOKO_WA>",
    "<GA>",
    "<POKEMON>",
    "<BOLD_A>",
    "<BOLD_B>",
    "<BOLD_C>",
    "<BOLD_D>",
    "<BOLD_E>",
    "<BOLD_F>",
    "<BOLD_G>",
    "<BOLD_H>",
    "<BOLD_I>",
    "<BOLD_V>",
    "<BOLD_S>",
    "<BOLD_L>",
    "<BOLD_M>",
    "<LV>",
    "<DO>",
    "<ID>",
}

# Pattern to find control codes in text
CONTROL_CODE_PATTERN = re.compile(r"<[^>]+>")

# Files/directories to check
CHECK_PATHS = [
    "data/text/",
    "engine/menus/",
]

# Files to exclude from checking
EXCLUDE_FILES = [
    "name_input_chars.asm",  # Name input has special formatting
    "mail_input_chars.asm",  # Mail input has special formatting
]


def get_visible_length(text):
    """
    Calculate the visible length of a text string, accounting for:
    - Control codes (don't count)
    - Multi-byte Vietnamese characters (count as 1)
    """
    # Remove control codes
    visible = CONTROL_CODE_PATTERN.sub("", text)

    # Count visible characters
    # Each character (including Vietnamese) counts as 1 tile
    return len(visible)


def check_file(filepath):
    """Check a single file for text lines exceeding max length."""
    errors = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        match = DB_STRING_PATTERN.match(line)
        if match:
            text = match.group(1)
            visible_len = get_visible_length(text)

            if visible_len > MAX_LINE_LENGTH:
                errors.append(
                    {
                        "file": filepath,
                        "line": line_num,
                        "text": text,
                        "length": visible_len,
                        "max": MAX_LINE_LENGTH,
                    }
                )

    return errors


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check text line lengths in assembly files"
    )
    parser.add_argument(
        "files", nargs="*", help="Specific files to check (default: check all)"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=MAX_LINE_LENGTH,
        help=f"Maximum line length (default: {MAX_LINE_LENGTH})",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Exit with 0 even if errors found (warnings only)",
    )
    args = parser.parse_args()

    max_length = args.max_length

    # Find project root (where Makefile is)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    all_errors = []

    if args.files:
        # Check specific files
        for filepath in args.files:
            if os.path.isfile(filepath):
                all_errors.extend(check_file(filepath))
    else:
        # Check default paths
        for check_path in CHECK_PATHS:
            full_path = project_root / check_path
            if full_path.is_dir():
                for asm_file in full_path.rglob("*.asm"):
                    if asm_file.name not in EXCLUDE_FILES:
                        all_errors.extend(check_file(str(asm_file)))
            elif full_path.is_file():
                if full_path.name not in EXCLUDE_FILES:
                    all_errors.extend(check_file(str(full_path)))

    # Filter by max_length if different from default
    if max_length != MAX_LINE_LENGTH:
        all_errors = [e for e in all_errors if e["length"] > max_length]
        for e in all_errors:
            e["max"] = max_length

    # Report errors
    if all_errors:
        print(
            f"Text length errors found ({len(all_errors)} lines exceed {max_length} characters):\n"
        )
        for error in all_errors:
            print(
                f"{error['file']}:{error['line']}: "
                f"length {error['length']} > {error['max']}"
            )
            print(f'  Text: "{error["text"]}"')
            print()

        if not args.warn_only:
            sys.exit(1)
    else:
        print(f"All text lines are within {max_length} characters.")

    sys.exit(0)


if __name__ == "__main__":
    main()
