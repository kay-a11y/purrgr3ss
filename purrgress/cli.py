"""
🐾 purrgress/cli.py - Personal Productivity CLI
-------------------------------------------------------

This is the central command-line interface (CLI) entrypoint for the `purrgress` suite -
a modular, customizable markdown automation and productivity tool.

Usage:
    purrgress <subcommand> [options]

Example:
    purrgress purrdate --file docs/purrboard.md --preview --write

-------------------------------------------------------

📦 Current Subcommands:
- purrdate
    Updates markdown files with current date/time info.
    Supports both {{TAGS}} and <!--DATE-XYZ--> anchor patterns.

    Options:
      -f, --file           Path to target markdown file
      --preview            Show unified diff before applying changes
      --write              Confirm writing changes to file
      --tags-only          Only replace {{TAGS}}, skip anchored blocks
      --anchors-only       Only replace anchors, skip {{TAGS}}

-------------------------------------------------------
"""

import argparse
from purrgress.scripts import purrdate

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="purrgress",
        description="🐾 Personal Productivity CLI - markdown, automation, and more.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ================================
    # SUBCOMMAND: purrdate
    # ================================
    pdate = subparsers.add_parser("purrdate", help="Update markdown files with current dates.")
    pdate.add_argument("-f", "--file", default="docs/purrboard.md",
        help="Target markdown file to update"
    )
    pdate.add_argument("--preview", action="store_true",
        help="Show diff preview before writing"
    )
    pdate.add_argument("--write", action="store_true",
        help="Actually write changes to file"
    )
    pdate.add_argument("--tags-only", action="store_true",
        help="Only replace {{TAGS}}, skip <!--DATE-XYZ--> blocks"
    )
    pdate.add_argument("--anchors-only", action="store_true",
        help="Only replace <!--DATE-XYZ--> anchors, skip {{TAGS}}"
    )

    args = parser.parse_args()

    if args.command == "purrdate":
        purrdate.run(
            file=args.file,
            preview=args.preview,
            write=args.write,
            tags_only=args.tags_only,
            anchors_only=args.anchors_only
        )

if __name__ == "__main__":
    main()
