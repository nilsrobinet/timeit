#!/bin/bash

set -euo pipefail

HOST="$1"

if [ -z "$HOST" ]; then
  echo "Usage: $0 <host>"
  exit 1
fi

echo "Deploying to $HOST"

ssh -T "$HOST" "mkdir -p ~/timeit/src ~/timeit/config ~/timeit/templates"

scp -r src/* "$HOST:~/timeit/src/"
scp -r config/* "$HOST:~/timeit/config/"
scp main.py "$HOST:~/timeit/"
scp -r templates/* "$HOST:~/timeit/templates/"
scp requirements.txt "$HOST:~/timeit/"

ssh -T "$HOST" << 'EOF'
set -euo pipefail

cd ~/timeit

if [ ! -d ~/timeit/venv ]; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Replace any previous app session so each deploy starts the latest code.
tmux kill-session -t timeit 2>/dev/null || true
tmux new-session -d -s timeit "cd ~/timeit && source ~/timeit/venv/bin/activate && python main.py >> ~/timeit/timeit.log 2>&1"

echo "TimeIt started in tmux session 'timeit'."
echo "Logs: ~/timeit/timeit.log"
EOF

echo "Deployment to $HOST completed."