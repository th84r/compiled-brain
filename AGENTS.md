# AGENTS.md

This repository is a knowledge library, and its instructions for any agent working in it are in [CLAUDE.md](CLAUDE.md). Read that file first and follow it. The file name is historical, the rules apply to every agent.

The operations are Markdown files in `.claude/commands/`. Read the one that matches the task and carry out its steps. The checks are plain Python in `.claude/scripts/` and need no particular model.

If your environment does not run `.claude/hooks/validate.py` automatically after each write, run it yourself on every page you change, or install it as a git pre-commit hook.
