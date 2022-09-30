# !/bin/bash
python3 -m oasis $1 $2
git add .
git commit -m "$(date +'Update %d %B %Y, %H:%M')"
git push
