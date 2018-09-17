# -*- coding: utf-8 -*-
""" Sum up JIRA work logs for a user in hours
  Usage:
    python jira_worklog_sum.py https://example.jira.com username password

  Example output:
    $ Total hours spent: 10.2
"""
from jiraextractor import JiraExtractor
from datetime import date
import sys
import xlsxwriter
import calendar
from itertools import groupby
from operator import itemgetter
from natsort import natsorted
import getopt


def get_uniq_keys(data):
  """ Create list of unique issue keys from the data. """
  uniq = []
  l = list({v['issueKey']:v for v in data}.values())
  for d in l:
    uniq.append(d['issueKey'])
  return uniq

def sum_up_worklog_for_a_day(data):
  """ Key function for aggregating the time spent in an issue a day. """
  grouper = itemgetter("issueKey", "dayStarted")
  result = []
  for key, grp in groupby(sorted(data, key = grouper), grouper):
    temp_dict = dict(zip(["issueKey", "dayStarted"], key))
    temp_dict["timeSpentSeconds"] = sum(item["timeSpentSeconds"] for item in grp)
    result.append(temp_dict)
  return result

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
  """ Convert seconds to hours """
  for i, data in enumerate(data_matrix):
    for j, time in enumerate(data):
      data_matrix[i][j] = round(time / 3600, 2)
  return data_matrix


def get_columns_sum(data_matrix):
  """ Sum up columns in a 2D data matrix """
  col_sums = []
  zipped = zip(*data_matrix)
  for d in zipped:
    col_sums.append(sum(d))
  return col_sums


def get_rows_sum(data_matrix):
  """ Sum up rows in a 2D data matrix """
  row_sums = []
  for i in range(len(data_matrix)):
    s = sum(data_matrix[i])
    row_sums.append(s)
  return row_sums


def create_description_matrix(logged_issues):
  description = []
  for issue in logged_issues:
    description.append(tuple((issue.key, issue.fields.summary)))
  return description


def generate_spreadsheet(data_matrix, workbook_name='worklog.xlsx', description_part_matrix=None, start_row=0, start_col=0):
  """ Generate spreadsheet from data matrix """
  workbook = xlsxwriter.Workbook(workbook_name)
  worksheet = workbook.add_worksheet()

  data_matrix = convert_seconds_to_hours(data_matrix)
  row_length = len(data_matrix)
  column_length = len(data_matrix[0])

  # Write key and summary
  desc_col_start_pos = start_col
  for i, desc in enumerate(description_part_matrix):
    for j, val in enumerate(desc):
      worksheet.write(start_row + i, desc_col_start_pos + j, val)

  # Write row totals
  row_totals_col_start_pos = desc_col_start_pos + j + 1
  row_sums = get_rows_sum(data_matrix)
  for i in range(row_length):
    worksheet.write(start_row + i, row_totals_col_start_pos, row_sums[i])
  worksheet.write(start_row + i + 1, row_totals_col_start_pos, sum(row_sums))

  # Write data
  data_col_start_pos = row_totals_col_start_pos
  for i, data in enumerate(data_matrix):
    for j, time in enumerate(data):
      worksheet.write(start_row + i, data_col_start_pos + 1 + j, time)

  # Write column totals
  col_sums = get_columns_sum(data_matrix)
  for i in range(column_length):
    worksheet.write(start_row + row_length, data_col_start_pos + 1 + i, col_sums[i])

  workbook.close()


def main(server_name, user_name, password):
  """ The main loop. """

  jira = JiraExtractor(server_name, user_name, password)

  logged_issues = jira.query_logged_issues()
  calendar_description_matrix = create_description_matrix(logged_issues)
  worklogs = jira.get_all_worklogs_for_issues(logged_issues)

  extracted_data = jira.extract_data_from_worklogs(worklogs)

  total_time_in_seconds = jira.get_worklogs_total_seconds(extracted_data)

  number_of_issues = len(logged_issues)
  last_day = jira.get_last_worklog_day(extracted_data)

  calendar_matrix_data = create_calendar_data_matrix(number_of_issues, last_day, extracted_data)

  generate_spreadsheet(calendar_matrix_data, output_name, calendar_description_matrix)
  print('Total hours spent:', total_time_in_seconds / 3600 )


def usage():
  print("""Options:
    -h --help
        Print this help.
    -s --server http://jira.example.com
        JIRA server address.
    -u --username UserName
        Username.
    -p --password SecretPassword
        Password.
  Usage Example:
    $ python jira_worklog_sum.py  -s https://example.jira.com -u username -p password
  """)

if __name__ == '__main__':
  output_name = 'jira-worklog-'+str(date.today())+'.xlsx'

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hs:u:p:o:', ['help', 'server=', 'username=' 'password=', 'output='])
  except getopt.GetoptError as err:
    print(err)
    usage()
    exit(1)

  for op, arg in opts:
    if op in ('-h', '--help'):
      usage()
      exit(1)
    elif op in ('-s', '--server'):
      server_name = arg
    elif op in ('-u', '--username'):
      user_name = arg
    elif op in ('-p', '--password'):
      password = arg
    elif op in ('-o', '--output'):
      print(arg)
      if arg[-4:] != 'xlsx':
        print('Invalid output filetype!')
        exit(1)
      output_name = arg
    else:
      assert False, "unhandled option"
  main(server_name, user_name, password)
