#!/bin/bash
# Asclepius Multi-Agent System - Frontend Startup Script
# Created by: CiscoPonce
# GitHub: https://github.com/CiscoPonce/Asclepius_Multiagent

cd "$(dirname "$0")"
python3 -m http.server 9051 --directory frontend
