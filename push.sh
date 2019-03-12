#/usr/bin/env bash

git add --all
git commit -v -m "Pull transcript from cnn10 $(date "+%Y-%m-%d")"
eval `ssh-agent`
ssh-add ~/.ssh/weak
git push -u origin master
eval `ssh-agent -k`
