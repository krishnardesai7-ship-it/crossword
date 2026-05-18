#!/usr/bin/env python
"""Run Django management commands from the repository root."""
import os
import sys
from pathlib import Path


def main():
    src_dir = Path(__file__).resolve().parent / "src"
    sys.path.insert(0, str(src_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
