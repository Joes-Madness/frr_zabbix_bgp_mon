#!/usr/bin/env python3
import subprocess
import sys
import json
import argparse
import os
import time

VAL_MAP = {
    "Established": -1,
    "Idle (Admin)": -2,
    "Idle (PfxCt)": -3,
    "Idle": -4,
    "Connect": -5,
    "Active": -6,
    "OpenSent": -7,
    "OpenConfirm": -8
}

JSONFILE = '/tmp/bgpmon.json'
CACHELIFE = 60
DISCOVERY_DYNAMIC = True

parser = argparse.ArgumentParser()
parser.add_argument("action", help="discovery | neighbor_stat")
parser.add_argument("stat", nargs='?', help="state | uptime | pfxSnt | pfxRcd", default="json")
parser.add_argument("-n", help="neighbor")
args = parser.parse_args()


def bgp_summary():
    result = []
    try:
        process = subprocess.Popen(
            ["vtysh", "-c", "show ip bgp summary json"], stdout=subprocess.PIPE)
    except IOError:
        print("ZBX_NOTSUPPORTED")
        sys.exit(1)

    out, err = process.communicate()
    result = json.loads(out.decode('utf-8'))

    with open(JSONFILE, 'w') as f:
        json.dump(result, f)

    return result

if __name__ == '__main__':
    json_cache = None
    result = None
    if os.path.exists(JSONFILE):
        time_cur_json = os.path.getmtime(JSONFILE)
        if time.time() - time_cur_json <= CACHELIFE:
            with open(JSONFILE) as f:
                json_cache = json.load(f)

    if args.action == 'neighbor_stat' and args.n:
        if not json_cache or not json_cache.get("ipv4Unicast"):
            json_cache = bgp_summary()

        if args.n in json_cache["ipv4Unicast"]["peers"]:
            n = json_cache["ipv4Unicast"]["peers"][args.n]
            if args.stat == 'state':
                result = VAL_MAP.get(n["state"])
            if args.stat == 'uptime':
                result = n["peerUptimeMsec"]
            if args.stat == 'pfxSnt':
                result = n["pfxSnt"]
            if args.stat == 'pfxRcd':
                result = n["pfxRcd"]
            if args.stat == 'json':
                result = {
                    'state': VAL_MAP.get(n["state"]),
                    'uptime': n["peerUptimeMsec"],
                    'pfxSnt': n["pfxSnt"],
                    'pfxRcd': n["pfxRcd"]
                }

    if args.action == 'discovery':
        if not json_cache or not json_cache.get("ipv4Unicast"):
            json_cache = bgp_summary()

        result = {"data": []}
        for n in json_cache["ipv4Unicast"]["peers"].items():
            description = n[1].get("desc", n[1].get("hostname", "No description"))
            dynamic = n[1].get("dynamicPeer", False)
            value = {
                "{#PEER_IP}": n[0],
                "{#DESCRIPTION}": description}
            if not dynamic or DISCOVERY_DYNAMIC:
                result["data"].append(value)

    if not result:
        print("ZBX_NOTSUPPORTED")
        sys.exit(1)

    print(json.dumps(result, indent=4, sort_keys=True))
