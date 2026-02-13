#!/bin/bash

source ./.venv/bin/activate
# python3 sketches.py

check_fzf() {

  if ! command -v fzf &> /dev/null; then
    echo "fzf is not installed"
    echo "go to https://github.com/junegunn/fzf"
    echo "please use git clone installation!"
    echo "otherwise you might get an outdated version 😿" 
    echo "required 0.48+"
    return 1
  fi

  local min_version=48
  local user_full_version=$(fzf --version)
  local user_version=$(echo ${user_full_version} | cut -d'.' -f2)

  if (( $user_version < $min_version )); then
    echo "required fzf 0.48+"
    echo "go to https://github.com/junegunn/fzf"
    echo "please use git clone installation!"
    echo "otherwise you might get an outdated version 😿" 
  else
    echo "🍰 Neat, yor fzf version is $user_full_version, min 0.48+ required, proceeding."
  fi
}

check_fzf

DATA=$(python3 sketches.py)

SELECTED=$(echo "$DATA" | fzf \
    --multi \
    --style full \
    --border --padding 1,1 \
    --border-label ' BBC Sound Effect Browser ' --input-label ' Input ' --header-label ' Info ' --preview-label ' Details 😼 ' \
    --color 'border:#aaaaaa,label:#cccccc' \
    --color 'preview-border:#9999cc,preview-label:#ccccff' \
    --color 'list-border:#669966,list-label:#99cc99' \
    --color 'input-border:#996666,input-label:#ffcccc' \
    --color 'header-border:#6699cc,header-label:#99ccff' \
    --layout reverse \
    --delimiter='│' \
    --with-nth=1 \
    --preview='echo "ID: {1}\nBeschreibung: {2}\nDauer: {3}"' \
    --preview-window=right:40% \
    --header="Leertaste=Markieren, Enter=Fertig" \
    --info=inline
    )

deactivate