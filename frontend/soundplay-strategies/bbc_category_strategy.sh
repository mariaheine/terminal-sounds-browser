# BBC CATEGORY SOUNDS STRATEGY

execute_strategy() {
  # 1. INIT FOCUS
  if [[ -f "${CURRENT_MPV_PROCESS_PID_FILE}" ]]; then

    last_pid=$(cat "${CURRENT_MPV_PROCESS_PID_FILE}" 2>/dev/null)
    if [[ -n "${last_pid}" ]] && kill -0 "${last_pid}" 2>/dev/null; then
      (kill "${last_pid}" 2>/dev/null) &
    fi

  fi

  sound_id="$1"
  echo "$sound_id" >"${CURRENT_FOCUSED_SONG_ID}"
  python3 -m backend.src.utils.logger "debug" "MEOW"

  # 2. MARK WAS LISTENED
  (
    sleep 1

    # sound_id=$(echo {} | cut -d"|" -f1)
    focused_song_id=$(cat "${CURRENT_FOCUSED_SONG_ID}")

    if [[ "${focused_song_id}" == "${sound_id}" ]]; then
      python3 -m backend.src.bbc.main set_was_listened "${sound_id}"
    fi
  ) &

  # 3. SOUND AUTOPLAY AND DOWNLOAD
  (
    sleep 0.35

    # sound_id=$(echo {} | cut -d"|" -f1)
    focused_song_id=$(cat "${CURRENT_FOCUSED_SONG_ID}")

    if [[ "${focused_song_id}" != "${sound_id}" ]]; then
      exit 0
    fi

    if [[ -f "${CURRENT_MPV_PROCESS_PID_FILE}" ]]; then
      final_last_pid=$(cat "${CURRENT_MPV_PROCESS_PID_FILE}" 2>/dev/null)
      if [[ -n "${final_last_pid}" ]] && kill -0 "${final_last_pid}" 2>/dev/null; then
        kill "${last_pid}" 2>/dev/null
        sleep 0.05
      fi
    fi

    filepath="${BBC_SOUNDS_CACHE_DIR}"/'"${sound_category}"'/"${sound_id}"

    if [[ -f "${filepath}.mp3" ]] && [[ ! -f "${filepath}.mp3.tmp" ]]; then

      mpv --no-video --no-terminal --loop=inf --title="${BBC_MPV_TAG}" "${filepath}.mp3" &
      echo "$!" >"${CURRENT_MPV_PROCESS_PID_FILE}" || {
        python3 -m frontend.src.main log "error" "Could not write MPV PID at ${CURRENT_MPV_PROCESS_PID_FILE}."
      }

    else

      python3 -m backend.src.bbc.main bbc_download_preview_sound "${sound_id}" '"${sound_category}"' &
      (
        while [[ -f "${filepath}.mp3.tmp" ]] || [[ ! -f "${filepath}.mp3" ]]; do
          sleep 0.5
        done

        current_focus_after_dl=$(cat "${CURRENT_FOCUSED_SONG_ID}" 2>/dev/null)

        if [[ "${current_focus_after_dl}" == "${sound_id}" ]]; then
          mpv --no-video --no-terminal --loop=inf --title="${BBC_MPV_TAG}" "${filepath}.mp3" &
          echo "$!" >"${CURRENT_MPV_PROCESS_PID_FILE}"
        fi
      ) &

    fi
  ) &
}
