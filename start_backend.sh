#!/bin/bash
# Asclepius Multi-Agent System - Backend Startup Script
# Created by: CiscoPonce
# GitHub: https://github.com/CiscoPonce/Asclepius_Multiagent

cd "$(dirname "$0")"
source agent_env/bin/activate
python backend/main.py
