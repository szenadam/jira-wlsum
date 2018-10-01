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
  Options:
    -h --help
        Print help.
    -s --server http://jira.example.com REQUIRED
        JIRA server address.
    -u --username UserName REQUIRED
        Username.
    -p --password SecretPassword REQUIRED
        Password.
    -c --csv
        Print csv to stdout.
    -t --sheet
        Generate spreadsheet.
    -o --output output.xlsx
        The output file name. Must end with .xlsx!
  Usage Example:
    $ python jira_worklog_sum.py  -s https://example.jira.com -u username -p password
```

## Example output:
```
$ Total hours spent: 10.2
```
Also there should be a file in the directory you executed the script. (E.g: `jira-worklog-2018-01-01.xlsx`)

## Run tests
```
$ pytest
```

## TODO:
  * FEATURE: Query a different users worklogs with admin
  * FEATURE: Write the required worklog hours in each month into the spreadsheet
  * FEATURE: Be able to read a txt file with the dates of holidays in a year
             and calculate the required worklog according to that.
  * FEATURE (long-term): Eventually should create a REST API around it. Maybe with Flask or Django
  * Spreadsheet should be optional if the user wants the output to stdout
  * Unit tests
