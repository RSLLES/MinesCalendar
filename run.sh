# !/bin/bash
python3 -m oasis
git add .
git commit -m "$(date +'Update %d %B %Y, %H:%M')"
git push