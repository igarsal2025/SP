#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git build-essential

if [ ! -d "SP" ]; then
  git clone https://github.com/igarsal2025/SP.git
fi

cd SP
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "Setup complete. Create /etc/sitec/sitec.env and install systemd units."
