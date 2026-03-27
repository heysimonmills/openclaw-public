#!/bin/bash

# Recipe batch processing script
# Process 16 Instagram recipe links

RECIPES=(
    "https://www.instagram.com/p/DJyb8auIEPG/"
    "https://www.instagram.com/p/DHUgn2bR3ca/"
    "https://www.instagram.com/p/DI2DH6_O-eA/"
    "https://www.instagram.com/p/DHCjTovp6re/"
    "https://www.instagram.com/p/DGg0tDyO-bq/"
    "https://www.instagram.com/p/DPf_v2ICERT/"
    "https://www.instagram.com/p/DRrVjhaEjbX/"
    "https://www.instagram.com/p/DR3G8YYCWWw/"
    "https://www.instagram.com/p/DTncR7NDrIa/"
    "https://www.instagram.com/p/DTYhjo7gV_5/"
    "https://www.instagram.com/p/DS2thMcD8eX/"
    "https://www.instagram.com/p/DRK8AwdCFnU/"
    "https://www.instagram.com/p/DRwN3FPEvBo/"
    "https://www.instagram.com/p/DQWr_I1EYag/"
    "https://www.instagram.com/p/DO6fFE1jt9-/"
    "https://www.instagram.com/p/DLMW4f7hetQ/"
)

cd /home/ubuntu/clawd/recipe-batch

for i in "${!RECIPES[@]}"; do
    NUM=$(printf "%02d" $((i+1)))
    URL="${RECIPES[$i]}"
    
    echo "=== Processing Recipe $NUM: $URL ==="
    
    # Download video
    echo "Downloading video..."
    yt-dlp -o "recipe_${NUM}.%(ext)s" "$URL" --no-update 2>&1 | tail -5
    
    # Find the downloaded video file
    VIDEO_FILE=$(ls recipe_${NUM}.* 2>/dev/null | head -1)
    
    if [ -z "$VIDEO_FILE" ]; then
        echo "ERROR: Failed to download recipe $NUM"
        echo "$URL" >> failed.txt
        continue
    fi
    
    # Extract audio
    echo "Extracting audio..."
    ffmpeg -i "$VIDEO_FILE" -vn -acodec mp3 -ar 16000 "recipe_${NUM}.mp3" -y 2>&1 | grep -E "(Duration|size=)" | tail -1
    
    if [ ! -f "recipe_${NUM}.mp3" ]; then
        echo "ERROR: Failed to extract audio for recipe $NUM"
        echo "$URL" >> failed.txt
        continue
    fi
    
    # Transcribe
    echo "Transcribing..."
    bash /home/ubuntu/.npm-global/lib/node_modules/clawdbot/skills/openai-whisper-api/scripts/transcribe.sh "recipe_${NUM}.mp3" --out "recipe_${NUM}_transcript.txt" 2>&1
    
    if [ ! -f "recipe_${NUM}_transcript.txt" ]; then
        echo "ERROR: Failed to transcribe recipe $NUM"
        echo "$URL" >> failed.txt
        continue
    fi
    
    # Save URL for reference
    echo "$URL" > "recipe_${NUM}_url.txt"
    
    echo "✓ Recipe $NUM completed"
    echo ""
done

echo "=== Batch processing complete ==="
echo "Total recipes: ${#RECIPES[@]}"
echo "Check failed.txt for any failures"
