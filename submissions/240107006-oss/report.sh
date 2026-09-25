#!/usr/bin/env bash

TARGET_DIR="${1:-.}"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Directory not found: $TARGET_DIR"
    exit 1
fi

# Переходим внутрь проверяемой директории
cd "$TARGET_DIR" || exit 1

# 1. Считаем файлы и директории
FILES_COUNT=$(find . -type f | wc -l)
DIRS_COUNT=$(find . -type d | wc -l)
# Вычитаем 1 для DIRS, чтобы не считать саму корневую папку '.'
DIRS_COUNT=$((DIRS_COUNT - 1))

echo "FILES: $FILES_COUNT"
echo "DIRS: $DIRS_COUNT"

# 2. Три самых больших файла (размер в байтах и относительный путь)
echo "LARGEST:"
find . -type f -exec du -b {} + | sort -rn | head -n 3 | sed 's|\./||'

# 3. Исполняемые файлы (сортировка по алфавиту)
echo "EXECUTABLE:"
find . -type f -executable | sed 's|\./||' | sort

# 4. Топ-5 расширений файлов
echo "EXTENSIONS:"
find . -type f -name '*.*' | sed -n 's/.*\.\([^.]*\)$/.\1/p' | sort | uniq -c | sort -rn | head -n 5 | awk '{print $1 " " $2}'
