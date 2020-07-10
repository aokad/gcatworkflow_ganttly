# gcatworkflow_ganttly
Plot gantt chart from GCATWorkflowCloud logs.

## Install

1. dependency

```
pip install plotly numpy boto3 awscli
aws configure ...
```

2. install

```
git clone https://github.com/aokad/gcatworkflow_ganttly.git
cd gcatworkflow_ganttly
```

## How to use

1. download AWS CloudWatch log

```
LOG_GROUP_PREFIX=/aws/batch/job
LOG_STREAM_PREFIX=gcatworkflow-cloud-run-job-definition/default/xxxxxxxxxxxx
DOWNLOAD_DIR=./
python ./download_log.py ${DOWNLOAD_DIR} ${LOG_GROUP_PREFIX} ${LOG_STREAM_PREFIX}
```

2. log ---> dataframe

```
LOG_PATH=./aws/batch/job/xxx.log
DF_PATH=./df.json
python ./log_to_df.py ${LOG_PATH} ${DF_PATH}
```

3. plot

```
DF_PATH=./df.json
python ./plot_gantt.py ${DF_PATH}
```

[example](./example.html)
