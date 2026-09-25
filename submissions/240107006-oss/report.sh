#!/usr/bin/env bash


set -euo pipefail

dir="${1:?usage: report.sh <directory>}"

# 1. FILES / DIRS
files_count=$(find "$dir" -type f | wc -l)
dirs_count=$(find "$dir" -mindepth 1 -type d | wc -l)

echo "FILES: $files_count"
echo "DIRS: $dirs_count"

# 2. LARGEST
echo "LARGEST:"
find "$dir" -type f -printf "%s %p\n" | sort -nr | head -n 3

# 3. EXECUTABLE
echo "EXECUTABLE:"
find "$dir" -type f -executable | sort

# 4. EXTENSIONS
echo "EXTENSIONS:"
find "$dir" -type f -name "*.*" | grep -o '\.[^.]*$' | sort | uniq -c | sort -nr | head -n 5 | awk '{print $1" "$2}'
