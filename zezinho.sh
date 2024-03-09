pgrep -f "discord_bot.py" > /dev/null

if [ $? -ne 0 ]; then
    echo "Bot is not running."
else
    echo "Killing the bot..."
    pkill -f "discord_bot.py"
fi

echo "Starting the bot..."
source .venv/bin/activate
python3 discord_bot.py &
disown
