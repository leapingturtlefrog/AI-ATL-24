#!/bin/bash

# Run by entering the command './push_simple.sh "commit message"'
# The commit message must be a string.
# Adds, commits, pulls, merges, and pushes code in just one command.
#
# Note on differences: This does not checkout a new branch or
# maintain only 5 local branches, unlike 'push.sh'
#
# Note: this script may not work if there is a merge conflict,
# which would have to be handled separately.

branch_name=$(git branch --show-current)
echo "$branch_name"

if [ ${#branch_name} -gt 0 ]; then
    git add . \
    && git commit -m "$1" \
    && git checkout main \
    && git pull origin main \
    && git merge "$branch_name" --no-edit \
    && git push -u origin main \
    && echo "Script successful" || echo "Script unsuccessful"
    echo "Please change to non-main branch"
else
    echo "Script unsuccessful. Current branch name was not read"
fi
