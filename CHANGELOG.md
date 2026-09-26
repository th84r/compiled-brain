# Changes

Each version is a git tag. What a library made from an earlier one can take over is said under each.

## v1.2.7

The loop and the shaping procedure stage the pages they changed by name, and commit as a separate command. Nothing stages everything any more, since another conversation may have work under way in the same library.

## v1.2.6

- The profile holds `owner:` and `language:`, so every later run knows whose books these are and which language to answer in.
- The template's own pages, the eval set, the page template, the voice page, open questions and the frontmatter schema, get titles in the owner's language at onboarding.
- The fictional example page moves to `wiki/archive/` in the same posting as the first real case, instead of showing as active work.
- Onboarding stages by name.

## v1.2.5

The permission lists narrowed to what a job needs. The library's own scripts are allowed by name, and nothing that writes where it likes.

## v1.2.4

A self-test in CI for every push.

## v1.2.3

The page template moved to `wiki/workflows/page-template.md`, outside `.claude/`, which Claude Code never lets an unattended run change.

## v1.2.2

The permissions that setting up and daily work need, found by running the first start against Claude Code.

## v1.2.1

Edit rules instead of Write rules. Claude Code ignores `Write(path)` rules with a warning, and an `Edit(path)` rule covers every tool that writes a file.

## v1.2

A contract with apps that read the library (`fmquery.py --contract`, `--json`), a balance held commit by commit, and key figures checked across pages.
