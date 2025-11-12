#!/bin/bash
# Script to run the agent in interactive CLI mode
# Note: Type "exit" to exit the interactive mode

# Go to project root
cd "$(dirname "$0")/.." || exit

# Run CLI
adk run agents/day_1b_multi_agents_pattern4_loop