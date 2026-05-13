# Skill Setup on Another Machine

This document explains how to install and use the `python-expert-skill` on a different machine.

## Files to Copy

- Skill source (folder): `~/.codex/skills/python-expert-skill`
- Packaged skill (file): `~/.codex/skills/dist/python-expert-skill.skill`

You can copy either the folder (editable) or the `.skill` package (portable).

## Option A: Install from the Folder (editable)

1) Copy the folder to the same location on the new machine:

```
~/.codex/skills/python-expert-skill
```

2) Restart Codex (or reload skills).

## Option B: Install from the .skill Package (portable)

1) Copy the file to the new machine:

```
~/.codex/skills/dist/python-expert-skill.skill
```

2) Use your Codex skill installer (or UI) to import the `.skill` file.

## Notes

- The skill name is `python-expert-skill`.
- If you change `SKILL.md`, re-run validation and packaging before distributing.
