#!/bin/bash
# Restart backend to apply Telegram notification changes
# Run with: sudo bash /home/temrjan/ai-avangard/restart_backend.sh

echo "Restarting AI-Avangard backend..."
systemctl restart ai-avangard-backend 2>/dev/null || supervisorctl restart ai-avangard 2>/dev/null || echo "Note: Please restart backend manually"
echo "Done!"
echo ""
echo "To test: Register a new user at http://temrjan.com/register"
echo "You should receive a Telegram notification."
