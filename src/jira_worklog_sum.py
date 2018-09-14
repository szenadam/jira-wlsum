# -*- coding: utf-8 -*-
""" Sum up JIRA work logs for a user in hours
  Usage:
    python jira_worklog_sum.py https://example.jira.com username password

  Example output:
    $ Total hours spent: 10.2
"""
from jira import JIRA
from datetime import datetime, date
import dateutil.parser
import pytz
import sys
import xlsxwriter
import calendar
from dateutil.tz import tzlocal
from itertools import groupby
from operator import itemgetter


def check_arguments_number():
  """ TODO: Later will be removed when getopts is implemented. """
  if len(sys.argv) < 3:
    print('Not enough arguments!\nUsage: python jira_worklog_sum.py https://example.jira.com username password')
    exit(1)


def query_logged_issues():
  """ Query the issues where worklogs were made by the currently logged in user
    TODO: Later should handle dates if teh user is interested in a different time range.
  """
  logged_issues = jira.search_issues('worklogAuthor = currentUser() AND worklogDate >= startOfMonth() ORDER BY key ASC')
  return logged_issues


def get_all_worklogs_for_issues(issues):
  """ Extract all worklog objects into a list. Add issue key to the worklog object. """
  worklogs = []
  for issue in issues:
    for worklog in jira.worklogs(issue.key):
      worklog.key = issue.key
      worklogs.append(worklog)
  return worklogs


def extract_data_from_worklogs(worklogs):
  """ Extract only the necessary attribues from the worklog objects. """
  data = []
  for worklog in worklogs:
    d = {}
    d['issueKey'] = worklog.key
    # The results should be in the local timezone. JIRA stores it in UTC0
    d['dayStarted'] = dateutil.parser.parse(worklog.started).astimezone(tzlocal()).day
    d['timeSpentSeconds'] = worklog.timeSpentSeconds
    data.append(d)
  return data


def get_last_worklog_day(data):
  """ Last day that has a worklog. Used for the calendar matrix width. """
  last_day = 0
  for d in data:
    if d['dayStarted'] > last_day:
      last_day = d['dayStarted']
  return last_day


def sum_up_worklog_for_a_day(data):
  """ Key function for aggregating the time spent in an issue a day. """
  grouper = itemgetter("issueKey", "dayStarted")
  result = []
  for key, grp in groupby(sorted(data, key = grouper), grouper):
    temp_dict = dict(zip(["issueKey", "dayStarted"], key))
    temp_dict["timeSpentSeconds"] = sum(item["timeSpentSeconds"] for item in grp)
    result.append(temp_dict)
  return result


def get_worklogs_total_seconds(data):
  """ Sum up all the time spent. """
  total = 0
  for d in data:
    total += d['timeSpentSeconds']
  return total


def main():
  """ The main loop. Loop through all logged issues in this month by the currentUser
  then loop through all the worklogs in that issue. """

  logged_issues = query_logged_issues()

  worklogs = get_all_worklogs_for_issues(logged_issues)

  extracted_data = extract_data_from_worklogs(worklogs)

  total_time_in_seconds = get_worklogs_total_seconds(extracted_data)

  number_of_issues = len(logged_issues)
  last_day = get_last_worklog_day(extracted_data)
  w, h = last_day, number_of_issues
  calendar_matrix = [[0 for x in range(w)] for y in range(h)]

  summed_up_data = sum_up_worklog_for_a_day(extracted_data)

  print('Total hours spent:', total_time_in_seconds / 3600 )


if __name__ == '__main__':
  check_arguments_number()
  server_name=sys.argv[1]
  user_name=sys.argv[2]
  password=sys.argv[3]
  jira = JIRA(server_name, basic_auth=(user_name, password))
  main()
