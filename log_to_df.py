import sys

# /path/to/log.txt
log_path = sys.argv[1]
df_path = sys.argv[2]
#log_path = "./log.txt"
#df_path = "./df.json"

def __pop_name(text):
    name = ""
    for t in text:
        if t == "[":
            name = ""
        elif t == "]":
            return name
        else:
            name += t
    return None

def __split_row(row):
    words = row.split(" ")
    day = day = words[0]
    time = time = words[1].split(".")[0]
    job_name = __pop_name(words[2])
    task_name = job_name.split(":")[0]
    return ("%s %s" % (day, time), job_name, task_name)

tasks = {}
skip = True
for row in open(log_path).readlines():
    row = row.split("\t")[-1].replace("b\'", "").rstrip()
    if row.startswith(">>>"):
        skip = False
        continue
        
    if skip:
        continue
    
    if row.find("checking s3 bucket") >= 0:
        (date, job_name, task_name) = __split_row(row)
        if not task_name in tasks:
            tasks[task_name] = {
                "Submit": date,
                "Jobs": {}
            }
    elif row.find("Instance Type:") >= 0:
        (date, job_name, task_name) = __split_row(row)
        if not job_name in tasks[task_name]["Jobs"]:
            tasks[task_name]["Jobs"][job_name] = {
                "Start": date,
                "Finish": "",
                "Resource": "running",
                "Jobnumber": len(tasks[task_name]["Jobs"])
            }
    elif row.find("tasks-stopped with") >= 0:
        (date, job_name, task_name) = __split_row(row)
        exit_code = "failure"
        if __pop_name(row.split(" ")[-1]) == "0":
            exit_code = "success"
            
        tasks[task_name]["Jobs"][job_name]["Resource"] = exit_code
    
    elif row.find("=== download metrics files start ===") >= 0:
        (date, job_name, task_name) = __split_row(row)
        tasks[task_name]["Jobs"][job_name]["Finish"] = date
        if tasks[task_name]["Jobs"][job_name]["Resource"] == "running":
            tasks[task_name]["Jobs"][job_name]["Resource"] = "failure"

import datetime
now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

df = []
for task in sorted(tasks.items(), key=lambda x:x[1]["Submit"]):
    for job in sorted(tasks[task[0]]["Jobs"].items(), key=lambda x:x[1]["Jobnumber"]):
        
        finish = tasks[task[0]]["Jobs"][job[0]]["Finish"]
        if finish == "":
            finish = now
            
        df.append({
            "Start": tasks[task[0]]["Jobs"][job[0]]["Start"],
            "Finish": finish,
            "Resource": tasks[task[0]]["Jobs"][job[0]]["Resource"],
            "Task": job[0]
        })

import json
json.dump(df, open(df_path, "w"), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
