#!/usr/bin/env bash

set -euo pipefail

# todo: check python installation and version, check venv, check if things are installed
# source ./.venv/bin/activate

# Finde das Projekt-Root (wo dieses Skript liegt)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "📁 Projekt-Root: $PROJECT_ROOT"

# Aktiviere venv
source "$PROJECT_ROOT/.venv/bin/activate"

export PYTHONPATH="${PYTHONPATH:-}:$PROJECT_ROOT"
echo "🔧 PYTHONPATH: $PYTHONPATH"

# Clear the log file
mkdir -p "${HOME}/.cache/terminal-effect-browser/logs"
> "${HOME}/.cache/terminal-effect-browser/logs/last.log"

echo $0

check_fzf() {

  if ! command -v fzf &> /dev/null; then
    echo "ERROR: fzf is not installed"
    echo "go to https://github.com/junegunn/fzf"
    echo "please use git clone installation!"
    echo "otherwise you might get an outdated version 😿" 
    echo "on Ubuntu with apt you will def get an outdated one"
    echo "required 0.48+"
    return 1
  fi

  local min_version=48
  local user_full_version=$(fzf --version)
  local user_version=$(echo ${user_full_version} | cut -d'.' -f2)

  if (( $user_version < $min_version )); then
    echo "ERROR: required fzf version 0.48+ while yours is $user_full_version"
    echo "go to https://github.com/junegunn/fzf"
    echo "please use git clone installation!"
    echo "otherwise you might get an outdated version 😿"
    echo "on Ubuntu with apt you will def get an outdated one"
    return 1
  else
    echo "🍰 Neat, yor fzf version is $user_full_version, min 0.48+ required, proceeding."
  fi
}

check_fzf

open_fzf_menu() {

  local config_name="$1"
  local -n config="$config_name"

  local data_array="${config[data_array]:-}"
  local use_multi="${config[use_multi]:-false}"
  local delimiter="${config[delimiter]:-' '}"
  local list_label="${config[list_label]:-'Listed Items'}"
  local info_label="${config[info_label]:-'Info'}"
  local info_content="${config[info_content]:-'Info Content'}"
  local preview_label="${config[preview_label]:-'Preview'}"
  local preview_content="${config[preview_content]:-'No preview set'}"

  local -n listed_elements="$data_array"
  
  #echo "DEBUG: RECONSTRUCTED contents: ${listed_elements[@]}" >&2

  local fzf_args=(
    # --sync
    --style full
    --border --padding 1,1
    --border-label "'° BBC Sound Effect Browser °'"
    --input-label "'° FUZZZ °'"
    --list-label "'° ${list_label} °'"
    --header="$info_content"
    --header-label "'° ${info_label} °'"
    --preview="$preview_content"
    --preview-label "'° ${preview_label} °'"
    --preview-window=right:40%
    --color 'border:#aaaaaa,label:#cccccc'
    --color 'preview-border:#9999cc,preview-label:#ccccff'
    --color 'list-border:#669966,list-label:#99cc99'
    --color 'input-border:#996666,input-label:#ffcccc'
    --color 'header-border:#6699cc,header-label:#99ccff'
    --layout reverse
    --with-nth=1 # TODO what was this
    --delimiter="$delimiter"
    --info=inline
  )

  # Add --multi conditionally
  if [[ "$use_multi" == "true" ]]; then
    fzf_args+=(--multi)
  fi

  # Convert listed_elements to a single multiline string
  # TODO This is pretty cool, make notes on printg and how the array is being passed here
  local fzf_input=$(printf '%s\n' "${listed_elements[@]}")

  local selection=$(echo "$fzf_input" | fzf "${fzf_args[@]}")

  echo $selection
} 

open_main_menu() {

  local readonly menu_option_1="Browse BBC Categories"
  local readonly menu_option_2="Show Favourites"
  local readonly menu_option_3="Settings"
  local readonly menu_option_4="Exit"

  local menu_elements=(
    "$menu_option_1"
    "$menu_option_2"
    "$menu_option_3"
    "$menu_option_4"
  )

  declare -A menu_config=(
    [data_array]='menu_elements'
    [use_multi]=false
    [preview_content]='echo "Category: {1}\nSize: {2}"'
    [delimiter]='\n'
    [info_label]='Info'
    [info_content]='[Arrows] Navigation [Enter] Confirm menu option.'
    [list_label]='Menu Options'
    [preview_label]='Option Info'
  )

  echo "DEBUG: Passing array name: menu_elements" >&2
  echo "DEBUG: Array contents: ${menu_elements[@]}" >&2

  local selected=$(open_fzf_menu 'menu_config')

  
  #echo "DEBUG: Selected: '$selected'" >&2
  #echo $selected

  case "${selected}" in
    "$menu_option_1")
      
      local bbc_categories=$(python3 -m src.main get_bbc_categories)

      declare -A bbc_categories_config=(
        [data_array]='bbc_categories'
        [use_multi]=false
        [preview_content]='echo "Category: {1}\nSize: {2}"'
        [delimiter]=' '
        [info_label]='Info'
        [info_content]='[Arrows] Navigate [Enter] Confirm selected category.'
        [list_label]='BBC Sound Effect Categories'
        [preview_label]='Category Info'
      )

      local category=$(open_fzf_menu 'bbc_categories_config')

      local category_name=$(echo "${category}" | cut -d' ' -f1)
      local category_size=$(echo "${category}" | cut -d' ' -f2)

      local sounds=$(python3 -m src.main get_bbc_sounds "${category_name}" "${category_size}")

      echo $sounds
      ;;
    *)
      echo "derp menu option: ${selected}"
      #mpv --no-video "./_NHU05104088.mp3"
      ;;
   esac
}

open_main_menu


deactivate
