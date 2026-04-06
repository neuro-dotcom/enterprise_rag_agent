#!/bin/bash

# 1. Build the brain
python build_brain.py

# 2. Wait 10 seconds for the network to settle
echo "Waiting for network stability..."
sleep 10

# 3. Start the bot
python main.py