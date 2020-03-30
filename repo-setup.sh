#!/usr/bin/env bash

email='dettmann@kth.se'
name='Aaron Dettmann'
origin='git@github.com-aarondettmann:airinnova/schemadict.git'

if [[ -z "$(git remote -v)" ]]; then
    git remote add origin "$origin"
else
    git remote set-url origin "$origin"
fi

git remote -v

git config user.email "$email"
git config user.name "$name"

