sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt update && sudo apt install -y ethereum

mkdir /etc/geth
cd data
geth --datadir /etc/geth/node1/ account import wallets/nodes/node1.key --password password.txt
cat password.txt > /etc/geth/password.txt

for i in {1..11}; do
  geth --datadir /etc/geth/node1/ account import wallets/teams/team$i.key --password password.txt
  cat password.txt >> /etc/geth/password.txt
done

for i in {1..50}; do
  geth --datadir /etc/geth/node1/ account import wallets/checker/checker$i.key --password password.txt
  cat password.txt >> /etc/geth/password.txt
done

geth --datadir /etc/geth/node1/ init genesis.json

cp -r wallets /etc/geth

cat << 'EOF' > /etc/geth/start.sh
tounlock="$(cat /etc/geth/wallets/teams/overall | awk '{ print $1 }' | tr '\n' ',' | sed 's/,$//'),$(cat /etc/geth/wallets/checker/overall | awk '{ print $1 }' | tr '\n' ',' | sed 's/,$//')"
/usr/bin/geth --datadir /etc/geth/node1/ --http --http.addr '0.0.0.0' --http.port 8545 --nodiscover --networkid 1337 --unlock "$(cat /etc/geth/wallets/nodes/overall | awk '{ print $1 }'),$tounlock" --mine --allow-insecure-unlock --password /etc/geth/password.txt
EOF

cat << 'EOF' > /etc/systemd/system/geth-node.service
[Unit]
Description=Geth
After=network.target

[Service]
Type=simple
User=root
Restart=always
RestartSec=12
ExecStart=/bin/bash /etc/geth/start.sh

[Install]
WantedBy=default.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart geth-node
