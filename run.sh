#!/bin/sh
# Запуск: ./run.sh [config.csv] [флаги]   Тесты: ./run.sh test
cd "$(dirname "$0")" || exit 1
if [ "$1" = "test" ]; then
    PYTHONPATH=src python3 -m unittest discover -s tests -v
else
    PYTHONPATH=src python3 src/main.py "$@"
fi
