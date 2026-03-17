#!/usr/bin/env bash

set -euo pipefail

#  ____                             __                    __
# /\  _`\                          /\ \__                /\ \__  __
# \ \ \/\_\    ___     ___     ____\ \ ,_\    __      ___\ \ ,_\/\_\    ___      __
#  \ \ \/_/_  / __`\ /' _ `\  /',__\\ \ \/  /'__`\  /' _ `\ \ \/\/\ \ /' _ `\  /'__`\
#   \ \ \L\ \/\ \L\ \/\ \/\ \/\__, `\\ \ \_/\ \L\.\_/\ \/\ \ \ \_\ \ \/\ \/\ \/\  __/
#    \ \____/\ \____/\ \_\ \_\/\____/ \ \__\ \__/.\_\ \_\ \_\ \__\\ \_\ \_\ \_\ \____\
#     \/___/  \/___/  \/_/\/_/\/___/   \/__/\/__/\/_/\/_/\/_/\/__/ \/_/\/_/\/_/\/____/
#
# Explanation 1. All those exported constants are such to make them readable in fzf subcontext.
# Explanation 2. All those temp files are necessary because we need some rw variable
#                while in fzf subcontext.
# Explanation 3. For common constants constants.py is the source of truth.

# PART 1. LOCAL CONSTANTS

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🗿 root: $SCRIPT_DIR"

source "$SCRIPT_DIR/.venv/bin/activate"

readonly PYTHONPATH="${PYTHONPATH:-}:$SCRIPT_DIR"
export PYTHONPATH

readonly AUTO_MODE_FILE="/tmp/tsb_auto_mode_$$" # $$ is process id
echo "false" >"$AUTO_MODE_FILE"
export AUTO_MODE_FILE

readonly CURRENT_MPV_PROCESS_PID_FILE="/tmp/tsb_current_mpv_pid_$$"
echo "" >"$CURRENT_MPV_PROCESS_PID_FILE"
export CURRENT_MPV_PROCESS_PID_FILE

readonly CURRENT_FOCUSED_SONG_ID="/tmp/tsb_current_focused_song_id_$$"
>"$CURRENT_FOCUSED_SONG_ID"
export CURRENT_FOCUSED_SONG_ID

readonly BBC_MPV_TAG="term-mpv-$$"
export BBC_MPV_TAG

# PART 2. COMMON CONSTANTS

readonly CONSTANTS=$(python3 -c "
from src.backend.constants import (
    VERSION,
    LOGS_DIR,
    LOG_FILE_NAME,
    BBC_SOUNDS_CACHE_DIR,
)
print(f'VERSION={VERSION}')
print(f'LOGS_DIR={LOGS_DIR}')
print(f'LOG_FILE_NAME={LOG_FILE_NAME}')
print(f'BBC_SOUNDS_CACHE_DIR={BBC_SOUNDS_CACHE_DIR}')
")

# TODO
while IFS= read -r line; do
  echo $line
  export "$line"
done <<<"$CONSTANTS"

#
#  ____    ___
# /\  _`\ /\_ \
# \ \ \/\_\//\ \      __     __      ___   __  __  _____
#  \ \ \/_/_\ \ \   /'__`\ /'__`\  /' _ `\/\ \/\ \/\ '__`\
#   \ \ \L\ \\_\ \_/\  __//\ \L\.\_/\ \/\ \ \ \_\ \ \ \L\ \
#    \ \____//\____\ \____\ \__/.\_\ \_\ \_\ \____/\ \ ,__/
#     \/___/ \/____/\/____/\/__/\/_/\/_/\/_/\/___/  \ \ \/
#                                                    \ \_\
# AND TRAP                                            \/_/

cleanup() {
  rm -f "$AUTO_MODE_FILE"
  rm -f "$CURRENT_MPV_PROCESS_PID_FILE"
  pkill -f "${BBC_MPV_TAG}" # kill running mpv processes
}

clear_log_file() {
  mkdir -p "${LOGS_DIR}"
  >"${LOGS_DIR}/${LOG_FILE_NAME}"
}

trap cleanup EXIT INT TERM KILL # is that an overkill?

check_fzf() {

  if ! command -v fzf &>/dev/null; then
    echo "🔥 ERROR: fzf is not installed"
    echo "go to https://github.com/junegunn/fzf"
    echo "please use git clone installation!"
    echo "otherwise you might get an outdated version 😿"
    echo "0.48+ is required"
    return 1
  fi

  local min_version=48
  local user_full_version=$(fzf --version)
  local user_version=$(echo ${user_full_version} | cut -d'.' -f2)

  if (($user_version < $min_version)); then
    echo "🔥 ERROR: required fzf version 0.48+ while yours is $user_full_version"
    echo "go to https://github.com/junegunn/fzf"
    echo "please use git clone installation!"
    echo "otherwise you might get an outdated version 😿"
    echo "0.48+ is required"
    return 1
  else
    echo "🍰 fzf version: {$user_full_version}, neat! min 0.48+ is required, proceeding."
  fi
}

#    ___            ___
#  /'___\         /'___\
# /\ \__/  ____  /\ \__/           ___ ___      __    ___   __  __
# \ \ ,__\/\_ ,`\\ \ ,__\_______ /' __` __`\  /'__`\/' _ `\/\ \/\ \
#  \ \ \_/\/_/  /_\ \ \_/\______\/\ \/\ \/\ \/\  __//\ \/\ \ \ \_\ \
#   \ \_\   /\____\\ \_\\/______/\ \_\ \_\ \_\ \____\ \_\ \_\ \____/
#    \/_/   \/____/ \/_/          \/_/\/_/\/_/\/____/\/_/\/_/\/___/
#

open_fzf_menu() {

  local config_name="$1"
  local -n config="$config_name"

  local -n data="${config[data]:-}"
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
  local strategy_name="${config[strategy_name]:-''}"

  #echo "DEBUG: RECONSTRUCTED contents: ${listed_elements[@]}" >&2
  python3 -m src.backend.common.logger "error" "meow"

  local fzf_args=(
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

    fzf_args+=(--bind 'right:execute(
        sound_id=$(echo {} | cut -d"|" -f1)
        python3 -m src.backend.bbc.main set_favourite "True" "${sound_id}" &
      )+refresh-preview')

    fzf_args+=(--bind 'left:execute(
        sound_id=$(echo {} | cut -d"|" -f1)
        python3 -m src.backend.bbc.main set_favourite "False" "${sound_id}" &
      )+refresh-preview')

    if [[ -n "$strategy_name" ]]; then

      # This sleep and check is to prevent unnecessary sourcing and strategy execution when
      # > fast scrolling down/up the sample list.
      # Sadly the glitch in fzf is persistent even after these measures.
      # An empty focus:execute() method already causes the glitch, so it seems beyond
      # > my capacity to fix it.
      # Only entirely disabling the focus:execute() method gets rid of the problem, but
      # > this project hangs around the possibility to perform actions on focus.
      # Unless im mistaken the problem is on the fzf side. Would be happy to be proven wrong,
      # > because this glitch annoys me as hell, I want to fast scroll s m o o t h .

      # fzf_args+=(--bind 'focus:execute()') # This also causes the glitch on fast scroll
      fzf_args+=(--bind 'focus:execute(
        sound_id=$(echo {} | cut -d"|" -f1)
        echo "$sound_id" >"${CURRENT_FOCUSED_SONG_ID}"
        (

          sleep 0.1
          focused_song_id=$(cat "${CURRENT_FOCUSED_SONG_ID}")
          if [[ "${focused_song_id}" != "${sound_id}" ]]; then
            exit 0
          fi

          source "./src/frontend/soundplay-strategies/'"${strategy_name}"'.sh"
          execute_strategy "$sound_id"
        ) &
     )')
    fi

    #
    # try with below which uses " and explicit escaping
    # when problem in bash or mac
    # fzf_args+=(--bind "f2:execute(
    #   if [[ \$(cat $AUTO_MODE_FILE) == \"true\" ]]; then
    #     echo false > $AUTO_MODE_FILE
    #   else
    #     echo true > $AUTO_MODE_FILE
    #   fi
    # )+refresh-preview")

    fzf_args+=(--bind 'f2:execute(
      if [[ $( cat "$AUTO_MODE_FILE" ) == "true" ]]; then
        echo false > "$AUTO_MODE_FILE"
      else
        echo true > "$AUTO_MODE_FILE"
      fi
    )+refresh-preview')

    preview_content+=';
      if [[ $( cat "$AUTO_MODE_FILE" ) == "true" ]]; then
        echo ""
        echo "AUTO MODE IS ON"
      fi
    '
  fi

  fzf_args+=(--preview "$preview_content")

  # OK, SO.
  # This is a neat little magic trick.
  # It works regardles if data is a string or an array.
  # Actually it mostly works when it is an array.
  # When it is a string it basically does nothing, only adds one \n newline at the end of it.
  # This works because stringy variable accessed with [@] just returns the full string.
  # But it transforms an array into an \n-separated string.
  # Which is what we want for fzf
  local fzf_input=$(printf '%s\n' "${data[@]}")

  local selection=$(echo "$fzf_input" | fzf "${fzf_args[@]}")

  echo $selection
}

open_bbc_categories_menu() {

  local bbc_categories=$(python3 -m src.backend.bbc.main bbc_get_categories)

  declare -A bbc_categories_config=(
    [data]='bbc_categories'
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

  echo $category

  if [[ -n "${category}" ]]; then
    local category_name=$(echo "${category}" | cut -d' ' -f1)
    local category_size=$(echo "${category}" | cut -d' ' -f2)
    open_bbc_sounds_list "${category_name}" "${category_size}"
  fi
}

open_bbc_sounds_list() {

  local category_name="${1}"
  local category_size="${2}"

  echo "📖 Loading BBC sounds list for category ${category_name}"
  local bbc_sounds=$(python3 -m src.backend.bbc.main bbc_get_sounds_data "${category_name}" "${category_size}")

  declare -A bbc_sound_list_config=(
    [data]='bbc_sounds'
    [use_multi]=true
    [preview_content]='
      id=$(echo {} | cut -d"|" -f1)
      description=$(echo {} | cut -d"|" -f2)
      original_favourite=$(echo {} | cut -d"|" -f4)
      echo " " # UMMMM, A LITTLE HACK cos i didnt figue out what causes the first echo to be sometimes printed twice
      echo "\e[0;97mID: \e[1;37m$id"
      echo "\e[0;97mDescription: \e[1;32m$description"
      echo ""
      
      fav=$(python3 -m src.backend.bbc.main is_favourite "$id")
      if [[ "$fav" == "True" ]]; then
        echo "\e[1;37mFAVORIT \e[5m⭐"
      fi
      #echo $original_favourite
      
      echo "\e[0;97m"
      echo "Comment: No I do not know how to get rid of the trailing | sign <3"
      '
    [delimiter]='|'
    [info_label]='Info'
    [info_content]='[Arrows] Navigate [Enter] Confirm selected category.'
    [list_label]="BBC Sound Effects for ${category_name} category"
    [preview_label]='Category Info'
    [with_nth]='5,2'
    [sample_list]=true
    [sound_category]="${category_name}"
    [strategy_name]="bbc_category_strategy"
  )

  open_fzf_menu 'bbc_sound_list_config' 1>/dev/null
  last_pid=$(cat "${CURRENT_MPV_PROCESS_PID_FILE}")
  if [[ -n "${last_pid}" ]] && kill -0 "${last_pid}" 2>/dev/null; then
    (kill "${last_pid}" 2>/dev/null) &
  fi
  open_bbc_categories_menu
}

open_show_favourites() {

  echo "📖 Loading BBC sounds list for category ${category_name}"
  local bbc_sounds=$(python3 -m src.backend.bbc.main bbc_get_sounds_data "${category_name}" "${category_size}")
  declare -A bbc_sound_list_config=(
    [data]='bbc_sounds'
    [use_multi]=true
    [preview_content]='
      id=$(echo {} | cut -d"|" -f1)
      description=$(echo {} | cut -d"|" -f2)
      original_favourite=$(echo {} | cut -d"|" -f4)
      echo " " # UMMMM, A LITTLE HACK cos i didnt figue out what causes the first echo to be sometimes printed twice
      echo "\e[0;97mID: \e[1;37m$id"
      echo "\e[0;97mDescription: \e[1;32m$description"
      echo ""
      
      fav=$(python3 -m src.backend.bbc.main is_favourite "$id")
      if [[ "$fav" == "True" ]]; then
        echo "\e[1;37mFAVORIT \e[5m⭐"
      fi
      #echo $original_favourite
      
      echo "\e[0;97m"
      echo "Comment: No I do not know how to get rid of the trailing | sign <3"
      '
    [delimiter]='|'
    [info_label]='Info'
    [info_content]='[Arrows] Navigate [Enter] Confirm selected category.'
    [list_label]="BBC Sound Effects for ${category_name} category"
    [preview_label]='Category Info'
    [with_nth]='5,2'
    [sample_list]=true
    [sound_category]="${category_name}"
  )
  open_fzf_menu 'bbc_sound_list_config' 1>/dev/null
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
    [data]='menu_elements'
    [use_multi]=false
    [preview_content]='echo "Category: {1}\nSize: {2}"'
    [delimiter]='\n'
    [info_label]='Info'
    [info_content]='[Arrows] Navigation [Enter] Confirm menu option.'
    [list_label]='Menu Options'
    [preview_label]='Option Info'
  )

  # echo "DEBUG: Passing array name: menu_elements" >&2
  # echo "DEBUG: Array contents: ${menu_elements[@]}" >&2

  while true; do
    local selected=$(open_fzf_menu 'menu_config')
    case "${selected}" in
    "$menu_option_1")
      open_bbc_categories_menu
      ;;
    "$menu_option_4")
      echo "Goodbaiii 🐱"
      break
      ;;
    *) ;;
    esac
  done
}

# echo '___  ___  ___                ________ ________  ___  _______   ________   ________  ___
# |\  \|\  \|\  \              |\  _____\\   __  \|\  \|\  ___ \ |\   ___  \|\   ___ \|\  \
# \ \  \\\  \ \  \             \ \  \__/\ \  \|\  \ \  \ \   __/|\ \  \\ \  \ \  \_|\ \ \  \
#  \ \   __  \ \  \  ___        \ \   __\\ \   _  _\ \  \ \  \_|/_\ \  \\ \  \ \  \ \\ \ \  \
#   \ \  \ \  \ \  \|\  \        \ \  \_| \ \  \\  \\ \  \ \  \_|\ \ \  \\ \  \ \  \_\\ \ \__\
#    \ \__\ \__\ \__\ \  \        \ \__\   \ \__\\ _\\ \__\ \_______\ \__\\ \__\ \_______\|__|
#     \|__|\|__|\|__|\/  /|        \|__|    \|__|\|__|\|__|\|_______|\|__| \|__|\|_______|   ___
#                  |\___/ /                                                                 |\__\
#                  \|___|/                                                                  \|__|'
#
# echo "🪤 download path unknown: Please enter download path for your favourite samples."
# echo "Tab to autocomplete, unexisting path will be mkdir'd."
# echo "If you mess up, go to your config."
# echo "🐖 It is in vi mode, you can't [Esc]ape it <evil laugher>"
#
# set -o vi # lol 🧨
#
# read -e -p "download path: " download_dir
# echo "selected download dir: $download_dir"

clear_log_file
check_fzf
open_main_menu
deactivate
