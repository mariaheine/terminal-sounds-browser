#!/usr/bin/env bash

set -euo pipefail

# Finde das Projekt-Root (wo dieses Skript liegt)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Projekt-Root: $SCRIPT_DIR"

source "$SCRIPT_DIR/.venv/bin/activate"
export PYTHONPATH="${PYTHONPATH:-}:$SCRIPT_DIR"
echo "🔧 PYTHONPATH: $PYTHONPATH"

# clear the log file
# to just use one and overwrite it on every run
mkdir -p "${HOME}/.cache/terminal-effect-browser/logs"
> "${HOME}/.cache/terminal-effect-browser/logs/last.log"

export AUTO_MODE_FILE="/tmp/tsb_auto_mode_$$" # $$ is process id
echo "false" > "$AUTO_MODE_FILE"

export CURRENT_MPV_PROCESS_PID_FILE="/tmp/tsb_current_mpv_pid_$$"
echo "" > "$CURRENT_MPV_PROCESS_PID_FILE"

export BBC_MPV_TAG="term-mpv-$$"
cleanup() {
  rm -f "$AUTO_MODE_FILE"
  pkill -f "${BBC_MPV_TAG}" # kill running mpv processes 
}
trap cleanup EXIT # TODO

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
    echo "🍰 fzf version: $user_full_version - Neat! Min 0.48+ is required, proceeding."
  fi
}

open_fzf_menu() {

  local config_name="$1"
  local -n config="$config_name"

  local data_array="${config[data_array]:-}"
  local use_multi="${config[use_multi]:-false}"
  local delimiter="${config[delimiter]:-''}"
  local with_nth="${config[with_nth]:-1}"
  local list_label="${config[list_label]:-'Listed Items'}"
  local info_label="${config[info_label]:-'Info'}"
  local info_content="${config[info_content]:-'Info Content'}"
  local preview_label="${config[preview_label]:-'Preview'}"
  local preview_content="${config[preview_content]:-'No preview set'}"
  local sample_list="${config[sample_list]:-false}"
  local sound_category="${config[sound_category]:-''}"
  # local bindings="${config[bindings]:-()}"


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
    --preview-label "'° ${preview_label} °'"
    --preview-window=right:40%:wrap
    --color 'border:#aaaaaa,label:#cccccc'
    --color 'preview-border:#9999cc,preview-label:#ccccff'
    --color 'list-border:#669966,list-label:#99cc99'
    --color 'input-border:#996666,input-label:#ffcccc'
    --color 'header-border:#6699cc,header-label:#99ccff'
    --layout reverse
    --delimiter="$delimiter"
    --with-nth="${with_nth}" # Which element by delimiter goes into the main list
    --info=inline
  )

  # Add --multi conditionally
  if [[ "$use_multi" == "true" ]]; then
    fzf_args+=(--multi)
  fi

  if [[ "$sample_list" == "true" ]]; then

    export SOUND_CATEGORY=$sound_category

    # TODO
    fzf_args+=(--bind 'ctrl-f:execute(
        sound_id=$(echo {} | cut -d"|" -f1)
        python3 -m src.main toggle_favourite "${sound_id}"
      )')
    fzf_args+=(--bind 'ctrl-f:+refresh-preview')
    fzf_args+=(--bind 'ctrl-d:execute(
        sound_id=$(echo {} | cut -d"|" -f1)
        python3 -m src.main bbc_download_preview_sound "${sound_id}" "${SOUND_CATEGORY}"
      )')
    
#       if [[ -n "$LAST_MPV_PID" ]] && kill -0 "$LAST_MPV_PID" 2>/dev/null; then
#   kill "$LAST_MPV_PID" 2>/dev/null  # Sofort, kein Durchsuchen
# fi

    # These mpv process PID gymnastics were necessary to neatly kill the process in background
    # So that the fzf window doesnt blick unpleasantly when the main process is blocked
    fzf_args+=(--bind 'focus:execute(

        last_pid=$( cat "${CURRENT_MPV_PROCESS_PID_FILE}" )
        kill "${last_pid}" &
        sound_id=$(echo {} | cut -d"|" -f1)
        filepath="$HOME"/.cache/terminal-effect-browser/sounds/bbc/"${SOUND_CATEGORY}"/"${sound_id}"

        if [[ -f "${filepath}.mp3" ]] && [[ ! -f "${filepath}.mp3.tmp" ]]; then
          mpv --no-video --no-terminal --loop=inf --title="${BBC_MPV_TAG}" "${filepath}.mp3" &
          echo "$!" > '"${CURRENT_MPV_PROCESS_PID_FILE}"'
        else
          python3 -m src.main bbc_download_preview_sound "${sound_id}" "${SOUND_CATEGORY}" &
          (
            while [[ -f "${filepath}.mp3.tmp" ]] || [[ ! -f "${filepath}.mp3" ]]; do
              sleep 0.5
            done
            mpv --no-video --no-terminal --loop=inf --title="${BBC_MPV_TAG}" "${filepath}.mp3" &
          ) &
        fi
      )')

    # try with below which uses " and explicit escaping
    # when problem in bash or mac
    # fzf_args+=(--bind "f2:execute(
    #   if [[ \$(cat $AUTO_MODE_FILE) == \"true\" ]]; then
    #     echo false > $AUTO_MODE_FILE
    #   else
    #     echo true > $AUTO_MODE_FILE
    #   fi
    # )+refresh-preview")

    # We cold not use the same simple export method as with SOUND_CATEGORY
    # Because we were only reading it
    # And we needed read/write here
    fzf_args+=(--bind 'f2:execute(
      if [[ $( cat '"$AUTO_MODE_FILE"' ) == "true" ]]; then
        echo false > '"$AUTO_MODE_FILE"'
      else
        echo true > '"$AUTO_MODE_FILE"'
      fi
    )+refresh-preview')

    preview_content+=';
      if [[ $( cat '"$AUTO_MODE_FILE"' ) == "true" ]]; then
        echo ""
        echo "AUTO MODE IS ON"
      fi
    '

  fi
    
  fzf_args+=(--preview "$preview_content")

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

  case "${selected}" in
    "$menu_option_1")
      
      local bbc_categories=$(python3 -m src.main bbc_get_categories)

      declare -A bbc_categories_config=(
        [data_array]='bbc_categories'
        [use_multi]=false
        [preview_content]='
            echo "\e[0;97mCategory: \e[1;32m{1}"
            echo "\e[0;97mSize: \e[1;32m{2}"
          '
        [delimiter]=' '
        [info_label]='Info'
        [info_content]='[Arrows] Navigate [Enter] Confirm selected category.'
        [list_label]='BBC Sound Effect Categories'
        [preview_label]='Category Info'
      )

      local category=$(open_fzf_menu 'bbc_categories_config')

      local category_name=$(echo "${category}" | cut -d' ' -f1)
      local category_size=$(echo "${category}" | cut -d' ' -f2)

      local bbc_sounds=$(python3 -m src.main bbc_get_sounds_data "${category_name}" "${category_size}")

      declare -A bbc_sounds_config=(
        [data_array]='bbc_sounds'
        [use_multi]=true
        [preview_content]='
          id=$(echo {} | cut -d"|" -f1)
          description=$(echo {} | cut -d"|" -f2)
          echo "\e[0;97mID: \e[1;37m$id"
          echo "\e[0;97mDescription: \e[1;32m$description"
          echo "\e[0;97mDrücke Ctrl-F zum Togglen"
          echo ""
          
          fav=$(python3 -m src.main is_favourite "$id")
          if [[ "$fav" == "1" ]]; then
            echo "\e[1;37mFAVORIT \e[5m⭐"
          fi
          
          echo "\e[0;97m"
          echo "Comment: No I do not know how to get rid of the trailing | sign <3"
          '
        [delimiter]='|'
        [info_label]='Info'
        [info_content]='[Arrows] Navigate [Enter] Confirm selected category.'
        [list_label]="BBC Sound Effects for ${category_name} category"
        [preview_label]='Category Info'
        [with_nth]=2
        [sample_list]=true
        [sound_category]="${category_name}"
        # [bindings_array]="sounds_bindings"
      )

      # sounds_bindings=(
      #     "ctrl-d:execute(
      #       sound_id=$(echo {} | cut -d"|" -f1)
      #       python3 -m src.main bbc_download_preview_sound \"\${sound_id}\" \"\${SOUND_CATEGORY}\"
      #     )"
      # )

      local sounds=$(open_fzf_menu 'bbc_sounds_config')
      # echo $sounds
      ;;
    *)
      echo "derp menu option: ${selected}"
      #mpv --no-video "./_NHU05104088.mp3"
      ;;
   esac
}

check_fzf
open_main_menu
deactivate
