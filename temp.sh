#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"

# Daten holen (ID│Beschreibung│Dauer)
DATA=$($VENV_PYTHON "$PROJECT_DIR/bbc_data.py" "$1" 2>/dev/null)

# fzf mit Beschreibung + Dauer in Liste, alle Daten im Preview
SELECTED=$(echo "$DATA" | fzf --multi \
    --delimiter='│' \
    --with-nth=2,3 \
    --preview='echo "ID: {1}\nBeschreibung: {2}\nDauer: {3}s"' \
    --preview-window=right:40% \
    --header="Leertaste=Markieren, Enter=Fertig")

# Extrahiere IDs
if [ ! -z "$SELECTED" ]; then
    SELECTED_IDS=$(echo "$SELECTED" | cut -d'│' -f1)
    echo "Ausgewählte IDs: $SELECTED_IDS"
    # ... download oder play
fi

---

#!/bin/bash

check_fzf_version() {
    local min_version=${1:-0.48.0}
    
    if ! command -v fzf &> /dev/null; then
        echo "❌ fzf ist nicht installiert!"
        echo "Bitte installiere fzf: https://github.com/junegunn/fzf"
        return 1
    fi
    
    local fzf_version=$(fzf --version | cut -d' ' -f1)
    
    # Einfacher String-Vergleich (funktioniert bei 0.x.y)
    if [[ "$fzf_version" < "$min_version" ]] && [[ ! "$fzf_version" == "$min_version" ]]; then
        echo "⚠️  Deine fzf Version: $fzf_version"
        echo "⚠️  Benötigt wird mindestens: $min_version"
        echo "⚠️  Bitte update fzf: https://github.com/junegunn/fzf"
        return 1
    fi
    
    echo "✅ fzf Version $fzf_version OK"
    return 0
}

# Verwendung
check_fzf_version "0.48.0" || exit 1

#!/bin/bash

# Hauptfunktion
bbc_menu() {
    local data=$(python3 bbc_data.py "${1:-Animals}" 2>/dev/null)
    
    # fzf mit Aktionen
    local result=$(echo "$data" | fzf \
        --delimiter='│' \
        --with-nth=2 \
        --preview='echo "ID: {1}\nBeschreibung: {2}\nDauer: {3}s\n\nAktionen: F2=Play, F3=Download, F4=Details"' \
        --preview-window='right:40%' \
        --header='F2=Play | F3=Download | F4=Details | Enter=Select' \
        --bind 'f2:become(play_sound {1})' \
        --bind 'f3:become(download_sound {1})' \
        --bind 'f4:become(show_details {1})')
}

# "become" ersetzt fzf mit dem Befehl - perfekt für Aktionen!
play_sound() {
    local id="$1"
    clear
    echo "▶ Spiele Sound $id"
    echo "Drücke 'q' zum Beenden"
    
    # Hier MP3 abspielen
    # mpv "https://sound-effects-media.bbcrewind.co.uk/mp3/$id.mp3" || return
    
    echo -e "\n🔙 Zurück zum Menü? (j/n)"
    read -n1
    [[ $REPLY == "j" ]] && bbc_menu  # Zurück ins Menü
}

download_sound() {
    local id="$1"
    echo "⬇ Downloade Sound $id nach ~/Downloads/"
    curl -o "$HOME/Downloads/$id.mp3" \
        "https://sound-effects-media.bbcrewind.co.uk/mp3/$id.mp3"
    echo "✅ Fertig!"
    sleep 1
    bbc_menu  # Zurück ins Menü
}