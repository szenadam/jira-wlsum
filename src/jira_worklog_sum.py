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
from natsort import natsorted

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


def is_in_this_month(time_created):
  """ Need to check each worklog, otherwise it would sum every time spent for the
  current user. Hopefully the worklog.created is in UTC0. """

  created = dateutil.parser.parse(time_created)
  today = datetime.today()
  if created > datetime(today.year,today.month,1,0,0,0,0,pytz.UTC):
    return True
  else:
    return False


def get_all_worklogs_for_issues(issues):
  """ Extract all worklog objects into a list. Add issue key to the worklog object. """
  worklogs = []
  for issue in issues:
    for worklog in jira.worklogs(issue.key):
      if is_in_this_month(worklog.started):
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


def get_uniq_keys(data):
  """ Create list of unique issue keys from the data. """
  uniq = []
  l = list({v['issueKey']:v for v in data}.values())
  for d in l:
    uniq.append(d['issueKey'])
  return uniq


def create_calendar_data_matrix(rows, columns, data):
  """ Create the calendar data matrix from an extracted worklog list.
    TODO: Needs to be simplified later for readability, modularity, etc.
  """
  calendar_matrix = [[0 for x in range(columns)] for y in range(rows)]
  summed_up_data = sum_up_worklog_for_a_day(data)
  sorted_data = natsorted(summed_up_data, key=lambda k: k['issueKey'])
  uniq_keys = get_uniq_keys(sorted_data)

  for i, key in enumerate(uniq_keys):
    for worklog in sorted_data:
      if worklog['issueKey'] == key:
        calendar_matrix[int(i)][int(worklog['dayStarted']-1)] = worklog['timeSpentSeconds']

  return calendar_matrix


def convert_seconds_to_hours(data_matrix):
  for i, data in enumerate(data_matrix):
    for j, time in enumerate(data):
      data_matrix[i][j] = round(time / 3600, 2)
  return data_matrix

def generate_spreadsheet(data_matrix, workbook_name, start_row=0, start_col=0):
  """ Generate spreadsheet from data matrix """
  workbook = xlsxwriter.Workbook(workbook_name)
  worksheet = workbook.add_worksheet()

  row_length = len(data_matrix)
  column_length = len(data_matrix[0])

  data_matrix = convert_seconds_to_hours(data_matrix)

  for i, data in enumerate(data_matrix):
    for j, time in enumerate(data):
      worksheet.write(start_row + i, start_col + j, time)

  col_sums = []
  zipped = zip(*data_matrix)
  for d in zipped:
    col_sums.append(sum(d))

  for i in range(column_length):
    worksheet.write(start_row + row_length, start_col + i, col_sums[i])

  workbook.close()


def main():
  """ The main loop. """

  logged_issues = query_logged_issues()

  worklogs = get_all_worklogs_for_issues(logged_issues)

  extracted_data = extract_data_from_worklogs(worklogs)

  total_time_in_seconds = get_worklogs_total_seconds(extracted_data)

  number_of_issues = len(logged_issues)
  last_day = get_last_worklog_day(extracted_data)
  calendar_matrix = create_calendar_data_matrix(number_of_issues, last_day, extracted_data)

  generate_spreadsheet(calendar_matrix, "examlpe.xlsx")
  print('Total hours spent:', total_time_in_seconds / 3600 )


if __name__ == '__main__':
  check_arguments_number()
  server_name=sys.argv[1]
  user_name=sys.argv[2]
  password=sys.argv[3]
  jira = JIRA(server_name, basic_auth=(user_name, password))
  main()
