# -*- coding: utf-8 -*-
""" Sum up JIRA work logs for a user in hours
  Usage:
    python jira_worklog_sum.py https://example.jira.com username password

  Example output:
    $ Total hours spent: 10.2

  TODO:
    * FEATURE: Generate and excel spread sheet
    * Spread should be optional if the user wants the output to stdout
    * Unit tests
    * Use getopts for arguments and option parsing
"""
from jira import JIRA
from datetime import datetime, date
import dateutil.parser
import pytz
import sys

server_name=sys.argv[1]
user_name=sys.argv[2]
password=sys.argv[3]
jira = JIRA(server_name, basic_auth=(user_name, password))

def check_arguments():
  """ TODO: Use it somewhere """
  if len(sys.argv) < 3:
    print('Usage: python jira_worklog_sum.py https://example.jira.com username password')
    exit(1)

def convert_to_seconds(s):
  """ Convert jira worklog format to seconds. Individual worklogs should only have
  '<number>d', '<number>h', '<number>s'"""

  seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
  return int(s[:-1]) * seconds_per_unit[s[-1]]

def read_time(time_spent):
  """ Read and convert jira worklog hours to seconds.
  TODO: What if the format is in '<number>d' or '<number>w' """

  total_seconds = 0
  if ' ' in time_spent:
    (h, m) = time_spent.split(' ')
    total_seconds += convert_to_seconds(h)
    total_seconds += convert_to_seconds(m)
  else:
    total_seconds += convert_to_seconds(time_spent)
  return total_seconds

def is_in_this_month(time_created):
  """ Need to check each worklog, otherwise it would sum every time spent for the
  current user. Hopefully the worklog.created is in UTC0. """

  created = dateutil.parser.parse(time_created)
  today = datetime.today()
  if created > datetime(today.year,today.month,1,0,0,0,0,pytz.UTC):
    return True
  else:
    return False

def is_author_the_same(name):
  return name == user_name

def main():
  """ The main loop. Loop through all logged issues in this month by the currentUser
  then loop through all the worklogs in that issue. """

  logged_issues = jira.search_issues('worklogAuthor = currentUser() AND worklogDate >= startOfMonth() ORDER BY key ASC')
  total_time_in_seconds = 0

  for issue in logged_issues:
    for worklog in jira.worklogs(issue.key):
      if is_in_this_month(worklog.created) and is_author_the_same(worklog.author.name):
        total_time_in_seconds += read_time(worklog.timeSpent)

  print('Total hours spent:', total_time_in_seconds / 3600 )

if __name__ == '__main__':
  main()
