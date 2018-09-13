JIRA Worklog Sum
================

## Usage:

```
$ python jira_worklog_sum.py https://example.jira.com username password
```

## Example output:
```
$ Total hours spent: 10.2
```

## TODO:
  * FEATURE: Generate and excel spread sheet
  * FEATURE: CSV output to stdout. E.g: key/summary/timespent(for every day, empty for none)
  * Spread should be optional if the user wants the output to stdout
  * Unit tests
  * Use getopts for arguments and option parsing
    * Option for total only
    * Option for CSV output
    * Option for xlsx output