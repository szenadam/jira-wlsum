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
import xlsxwriter
import calendar
from dateutil.tz import tzlocal

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

  workbook = xlsxwriter.Workbook('gomontir_jira.xlsx')
  worksheet = workbook.add_worksheet()
  worksheet.write('A1', server_name + ' worklog')
  worksheet.write('A2', user_name)
  worksheet.write('A3', 'Key')
  worksheet.write('B3', 'Summary')

  current_year = date.today().year
  current_month = date.today().month
  current_month_short_name = calendar.month_name[current_month][:3]
  start_of_this_month = date(current_year, current_month, 1)
  today = date.today()
  delta = today - start_of_this_month

  for i in range(1, delta.days + 2):
    worksheet.write(2, 1+i, current_month_short_name + ' ' + str(i).zfill(2))

  for j, issue in enumerate(logged_issues):

    for worklog in jira.worklogs(issue.key):
      if is_in_this_month(worklog.created) and is_author_the_same(worklog.author.name):
        worksheet.write(3+j, 0, issue.key)
        worksheet.write(3+j, 1, issue.fields.summary)

        day_created = dateutil.parser.parse(worklog.created).astimezone(tzlocal()).day
        worksheet.write(3+j, day_created + 1, read_time(worklog.timeSpent) / 3600)

        total_time_in_seconds += read_time(worklog.timeSpent)

  workbook.close()
  print('Total hours spent:', total_time_in_seconds / 3600 )


if __name__ == '__main__':
  main()
