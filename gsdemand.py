#!/usr/bin/python
from pygsstats import *
from pandas import DataFrame
import platform
import argparse
from datetime import datetime as dt
from datetime import timedelta



def get_demand_data(log):
    connections = find_all(PYGSS['CLIENT_ADDRESS'], log)
    data = []
    for conn in connections:
        start_pos = conn+len(PYGSS['CLIENT_ADDRESS'])+1
        end_pos = log.find(':', start_pos)
        ipaddr = log[start_pos:end_pos]
        loc = get_location(ipaddr)
        if loc:
            data.append(loc)
    return DataFrame(data)


def main(args):
    host_name = platform.node().split('.', 1)[0]
    now_time = dt.now()
    td = 0
    if args.day:
        td = args.day

    start_time = (now_time-timedelta(days=td)).strftime('%Y-%m-%d 00:00:00')
    end_time = (now_time-timedelta(days=td)).strftime('%Y-%m-%d 23:59:59')

    logdir = ''
    if args.logdir:
        logdir = args.logdir
    
    log = get_log_all(start_time, end_time, split=False, debug=args.debug, logdir=logdir)
    df = get_demand_data(log)
    df.groupby(['Region']).size().sort_values(ascending=False).to_excel("{}.xlsx".format(host_name))
    df.loc[df['Region'] == "Krasnoyarskiy Kray"].to_excel("{}-Krasnoyarsk.xlsx".format(host_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PlayKey GameServer demand analyzer')
    parser.add_argument('--day', type=int, action='store', dest="day", help='Which day to parse')
    parser.add_argument('--logdir', type=str, action='store', dest="logdir", help='Path to journal log dir')
    parser.add_argument('--debug', help='Print additional info during run', action='store_true', default=False)
    args = parser.parse_args()
    main(args)
