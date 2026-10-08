#!/usr/bin/env bash
# Generate one image with the Codex CLI (logged in with ChatGPT; check with: codex login status).
# usage: gen.sh <out.png> <ref-image-or-"none"> <prompt>
set -euo pipefail
out="$1"; ref="$2"; prompt="$3"
command -v codex >/dev/null || { echo "codex CLI not found: use the prompts in references/prompts.md in any image generator instead" >&2; exit 127; }
# Git Bash on Windows needs Windows-style paths for codex; elsewhere paths pass through unchanged
p() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
wd="$(mktemp -d)"; cwd="$(p "$wd")"
args=(exec --skip-git-repo-check -s workspace-write -C "$cwd")
[[ "$ref" != none ]] && args+=(-i "$(p "$ref")")
full="Use your image_generation tool to create an image.

PROMPT: ${prompt}

Requirements:
- You MUST call the image_generation tool. Do NOT write scripts or fabricate a PNG another way.
- Save the PNG as out.png in your current working directory (relative path). Reply with only the file name."
codex "${args[@]}" -- "$full" </dev/null >"$wd.log" 2>&1 || { tail -30 "$wd.log"; exit 1; }
img="$wd/out.png"; [[ -f "$img" ]] || img="$(ls -t "$wd"/*.png | head -1)"
cp "$img" "$out"; echo "$out"
