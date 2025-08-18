#!/bin/bash
# Stop any running Vite servers silently
pkill -f "vite.*7777" 2>/dev/null || true
pkill -f "npx vite" 2>/dev/null || true
exit 0