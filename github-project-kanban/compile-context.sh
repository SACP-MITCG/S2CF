#!/bin/bash

REPO="SACP-MITCG/S2CF"
OUTPUT="s2cf_llm_snapshot.md"

echo "Compiling GitHub state into $OUTPUT for LLM ingestion..."

# Initialise the Markdown file with metadata
echo "# Project State Snapshot: $REPO" > "$OUTPUT"
echo "**Generated:** $(date)" >> "$OUTPUT"
echo "---" >> "$OUTPUT"

# Pull all issues (Open and Closed) into memory safely
gh issue list --repo "$REPO" --state all --limit 100 --json number,title,state,body > temp_snapshot.json

# Parse and format into Markdown
jq -c '.[]' temp_snapshot.json | while IFS= read -r issue; do

  num=$(jq -r '.number' <<< "$issue")
  title=$(jq -r '.title' <<< "$issue")
  state=$(jq -r '.state' <<< "$issue")
  body=$(jq -r '.body' <<< "$issue")

  # Write the Issue Header and Body
  echo "## Issue #$num: $title [State: $state]" >> "$OUTPUT"
  echo "**Description/Body:**" >> "$OUTPUT"
  echo "$body" >> "$OUTPUT"
  echo "" >> "$OUTPUT"

  # Fetch the comment thread for this specific issue
  # We use jq to format it cleanly as a blockquote with the author's name
  comments=$(gh issue view "$num" --repo "$REPO" --json comments --jq '.comments[] | "> **" + .author.login + "** commented:\n> " + (.body | gsub("\n"; "\n> ")) + "\n"')

  if [ -n "$comments" ]; then
    echo "**Comment Thread:**" >> "$OUTPUT"
    echo "$comments" >> "$OUTPUT"
  else
    echo "*No comments yet.*" >> "$OUTPUT"
  fi

  echo "" >> "$OUTPUT"
  echo "---" >> "$OUTPUT"

done

# Clean up
rm temp_snapshot.json
echo "Compilation complete. File is ready to be dropped into Gemini."
