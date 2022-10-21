# Monitoring FRR BGP session  for zabbix

## Description
Descover and monitor BGP session with count of prefix or state like "Active" or Idle (Admin).
Trigger if session change state.

## Requirements
- Python
- Zabbix from 3.4 version

## Installation
- copy bgpmon.py to /usr/local/bin
- give execute bit `chmod +x /usr/local/bin/bgpmon.py`
- write file for zabbix agent for example /etc/zabbix/zabbix_agentd.d/userparameter_bgpd.conf
```sh
UserParameter=bgp.peers.discovery,/usr/local/bin/bgpmon.py discovery
UserParameter=bgp.peer.stat[*],/usr/local/bin/bgpmon.py -n $1 neighbor_stat $2
```
- Provide vtysh access to user zabbix
```
sudo usermod -a -G frrvty zabbix
```
- Restart zabbix-agent
```
systemctl restart zabbix-agent
```
- Import template file
