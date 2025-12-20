#!/bin/bash

# Download card images for Chkobba game
# Uses the deckofcardsapi.com static images

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cards_directory="$script_directory/public/cards"

mkdir -p "$cards_directory"

# Card suits: S=Spades, H=Hearts, D=Diamonds, C=Clubs
SUITS=("S" "H" "D" "C")

# Card ranks for Tunisian Chkobba: A, 2-10 (no J, Q, K)
RANKS=("A" "2" "3" "4" "5" "6" "7" "8" "9" "0")  # 0 = 10 in deckofcardsapi

echo "Downloading card images to $cards_directory..."

# Download card back
echo "Downloading card back..."
curl -s -o "$cards_directory/back.png" "https://deckofcardsapi.com/static/img/back.png"

# Download all cards
for suit in "${SUITS[@]}"; do
    for rank in "${RANKS[@]}"; do
        filename="${rank}${suit}.png"
        url="https://deckofcardsapi.com/static/img/${filename}"
        echo "Downloading $filename..."
        curl -s -o "$cards_directory/$filename" "$url"
    done
done

echo ""
echo "Download complete! Card images saved to $cards_directory"
echo "Total files: $(ls -1 "$cards_directory" | wc -l)"
