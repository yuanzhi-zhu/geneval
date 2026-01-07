#!/usr/bin/env bash
set -euo pipefail

FOLDER_A="SD1.5"
FOLDER_B="SD1.5_2"
OUT="SD1.5_combined"

mkdir -p "$OUT"

# Iterate subfolders present in A (assuming A and B have the same structure)
find "$FOLDER_A" -mindepth 1 -maxdepth 1 -type d -print0 | while IFS= read -r -d '' dirA; do
  sub="$(basename "$dirA")"
  dirB="$FOLDER_B/$sub"
  outDir="$OUT/$sub"

  if [[ ! -d "$dirB" ]]; then
    echo "Warning: missing in B: $dirB (skipping $sub)" >&2
    continue
  fi

  mkdir -p "$outDir/samples"

  # Copy metadata/grid (choose A as source of truth; adjust if you prefer)
  [[ -f "$dirA/metadata.jsonl" ]] && cp -p "$dirA/metadata.jsonl" "$outDir/"
  [[ -f "$dirA/grid.png"      ]] && cp -p "$dirA/grid.png"      "$outDir/"


  # copy 00000-00031 from A and B into 00000-00063 in outDir
  
  # Copy A samples to 00000-00031
  for i in {0..31}; do
    src="$dirA/samples/$(printf "%05d.png" "$i")"
    dst="$outDir/samples/$(printf "%05d.png" "$i")"
    if [[ -f "$src" ]]; then
      cp -p "$src" "$dst"
    else
      echo "Warning: missing A sample: $src" >&2
    fi
  done

  # Copy B samples to 00032-00063
  for i in {0..31}; do
    src="$dirB/samples/$(printf "%05d.png" "$i")"
    dst="$outDir/samples/$(printf "%05d.png" "$((i+32))")"
    if [[ -f "$src" ]]; then
      cp -p "$src" "$dst"
    else
      echo "Warning: missing B sample: $src" >&2
    fi
  done
done

echo "Done. Merged dataset written to: $OUT"