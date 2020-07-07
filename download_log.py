# -*- coding: utf-8 -*-
"""
Created on Tue Apr 03 16:02:38 2018

@author: Okada

python download_log.py ./ log_group_prefix log_stream_prefix OPTION:tail
"""

import sys
import os
import boto3
import datetime

def _timestamp(text):
   return datetime.datetime.fromtimestamp(int(text)/1000).strftime("%Y%m%d_%H%M%S")

def _describe_log_groups(logGroupNamePrefix, nextToken, limit):

    for i in range(3):
        try:
            if nextToken == None:
                print("boto3.client('logs').describe_log_groups(logGroupNamePrefix = '%s', limit = %d)" % (logGroupNamePrefix, limit))
            
                groups = boto3.client('logs').describe_log_groups(
                    limit = limit, 
                    logGroupNamePrefix = logGroupNamePrefix
                )
                print ("log-groups: %d" % (len(groups["logGroups"])))
                
            else:
                groups = boto3.client('logs').describe_log_groups(
                    limit = limit, 
                    logGroupNamePrefix = logGroupNamePrefix,
                    nextToken = nextToken
                )
            
            return groups
        
        except Exception:
            pass
    return None

def _describe_log_streams(logGroupName, logStreamNamePrefix, nextToken, limit):
    
    for i in range(3):
        try:
            if nextToken == None:
                print ("boto3.client('logs').describe_log_streams(logGroupName = '%s', logStreamNamePrefix = '%s', limit = %d)" % (logGroupName, logStreamNamePrefix, limit))
                
                streams = boto3.client('logs').describe_log_streams(
                    logGroupName = logGroupName,
                    logStreamNamePrefix = logStreamNamePrefix,
                    limit = limit
                )
                print ("log-streams: %d" % (len(streams["logStreams"])))
                
            else:
                streams = boto3.client('logs').describe_log_streams(
                    logGroupName = logGroupName,
                    logStreamNamePrefix = logStreamNamePrefix,
                    limit = limit,
                    nextToken = nextToken
                )
            
            return streams
        
        except Exception:
            pass
    return None

def _get_log_events(logGroupName, logStreamName, nextToken):
    
    for i in range(3):
        try:
            if nextToken == None:
                print ("boto3.client('logs').get_log_events(logGroupName = '%s', logStreamName = '%s', startFromHead = True)" % (logGroupName, logStreamName))
                
                events = boto3.client('logs').get_log_events(
                    logGroupName = logGroupName,
                    logStreamName = logStreamName,
                    startFromHead = True
                )
                print ("log-events: %d" % (len(events["events"])))
                
            else:
                events = boto3.client('logs').get_log_events(
                    logGroupName = logGroupName,
                    logStreamName = logStreamName,
                    startFromHead = True,
                    nextToken = nextToken
                )
        
            return events
        
        except Exception:
            pass
    return None

def _get_log_events_tail(logGroupName, logStreamName):

    for i in range(3):
        try:
            print ("boto3.client('logs').get_log_events(logGroupName = '%s', logStreamName = '%s', startFromHead = True)" % (logGroupName, logStreamName))
            
            events = boto3.client('logs').get_log_events(
                logGroupName = logGroupName,
                logStreamName = logStreamName,
                startFromHead = False
            )
            print ("log-events: %d" % (len(events["events"])))
        
            return events
        except Exception:
            pass
    return None

# specify Log stream
def _download_log_stream(log_group_name, stream, wdir, tail = False):

    output_dir = "%s/%s" % (wdir.rstrip("/"), log_group_name)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception:
            pass
            
    f = open("%s/%s-%s.log" % (
        output_dir,
        stream["logStreamName"].split("/")[1],
        _timestamp(stream["creationTime"])), "w")
    
    if tail:
        events = _get_log_events_tail(log_group_name, stream["logStreamName"])
        if events  != None:
            for event in events["events"]:
                f.write("%s\t%s\n" % (_timestamp(event["timestamp"]), event["message"].encode('utf-8')))
    else:
        events = None
        while(1):
            if events != None and len(events["events"]) == 0:
                break
    
            if events == None:
                events = _get_log_events(log_group_name, stream["logStreamName"], None)
            else:
                events = _get_log_events(log_group_name, stream["logStreamName"], events["nextForwardToken"])
            
            if events  != None:
                for event in events["events"]:
                    f.write("%s\t%s\n" % (_timestamp(event["timestamp"]), event["message"].encode('utf-8')))
        
    f.close()

def download_logs(wdir, log_group_prefix, log_stream_prefix, tail):
    
    group = None
    while(1):
        if group != None and not "nextToken" in group.keys():
            break

        if group == None:
            group = _describe_log_groups(log_group_prefix, None, 1)
        else:
            group = _describe_log_groups(log_group_prefix, group["nextToken"], 1)
        
        if group == None:
            break
        if len(group["logGroups"]) == 0:
            break
        
        stream = None
        while(1):
            if stream != None and not "nextToken" in stream.keys():
                break

            if stream == None:
                stream = _describe_log_streams(group["logGroups"][0]["logGroupName"], log_stream_prefix, None, 1)
            else:
                stream = _describe_log_streams(group["logGroups"][0]["logGroupName"], log_stream_prefix, stream["nextToken"], 1)
            
            if stream == None:
                break
            if len(stream["logStreams"]) == 0:
                break
            
            _download_log_stream(group["logGroups"][0]["logGroupName"], stream["logStreams"][0], wdir, tail)

def main():
    wdir = sys.argv[1]
    log_group_prefix = sys.argv[2]
    log_stream_prefix = sys.argv[3]
    tail = len(sys.argv) > 4
        
    print ("=== download log files start ===")
    download_logs(wdir, log_group_prefix, log_stream_prefix, tail)
    print ("=== download log files end ===")

    
if __name__ == "__main__":
    main()
