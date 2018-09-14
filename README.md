JIRA Worklog Sum
================

## Description

Sum your logged hours in JIRA for the current month.

## Install dependencies
```
$ pip install -r requirements.txt
```

## Usage:
```
$ python jira_worklog_sum.py https://example.jira.com username password
```

## Example output:
```
$ Total hours spent: 10.2
```

## Run tests
```
$ pytest
```

## TODO:
  * FEATURE: Generate and excel spread sheet
  * FEATURE: CSV output to stdout. E.g: key/summary/timespent(for every day, empty for none)
  * FEATURE: Query a different users worklogs with admin
  * LONGTERM FEATURE: Eventually should create a REST API around it. Maybe with Flask or Django
  * Spreadsheet should be optional if the user wants the output to stdout
  * Unit tests
  * Use getopts for arguments and option parsing
    * Option: total only
    * Option: stdout output
    * Option: CSV output
    * Option: xlsx output
    * Argument: server
    * Argument: username
    * Argument: password
