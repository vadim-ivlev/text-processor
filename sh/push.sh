#!/bin/bash

git add -A .
git commit -m "."
# git push github master
git push origin --all
git push gitlab --all
git push github --all