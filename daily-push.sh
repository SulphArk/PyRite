#!/bin/bash
cd ~/Projects/PyRite
git add -A
git commit -m "Daily update: $(date +%Y-%m-%d)"
git push
echo "Pushed to GitHub!"
