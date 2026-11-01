#!/bin/bash
# One command: bash run_batch.sh <batch-name> [n]
cd /home/claude/np/factory && python3 orchestrate.py "$1" "${2:-5}" > "runs/$1.out" 2>&1
tail -n 25 "runs/$1/log.txt"
