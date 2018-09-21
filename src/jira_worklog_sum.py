# -*- coding: utf-8 -*-
""" Sum up JIRA work logs for a user in hours
  Usage:
    python jira_worklog_sum.py https://example.jira.com username password

  Example output:
    $ Total hours spent: 10.2
"""
from jiraextractor import JiraExtractor
from worklogmatrix import WorklogMatrix

from datetime import date
import calendar
import sys
import xlsxwriter
import getopt
import csv


def generate_spreadsheet(extracted_data, workbook_name='worklog.xlsx', start_row=0, start_col=0):
    """ Generate spreadsheet from data matrix """
    workbook = xlsxwriter.Workbook(workbook_name)
    worksheet = workbook.add_worksheet()

    worklogmatrix = WorklogMatrix(extracted_data)

    # Write headers
    headers = ['Key', 'Summary', 'Sum']
    for i, h in enumerate(headers):
        worksheet.write(start_row, start_col + i, h)
    t = date.today()
    m = calendar.month_abbr[t.month]
    for i in range(t.day): # Write month and days
        day = str(i+1).zfill(2)
        worksheet.write(start_row, 3 + i, "{0} {1}".format(m ,day))

    # Write key and summary
    desc_row_start_pos = start_row + 1
    desc_col_start_pos = start_col
    for i, desc in enumerate(worklogmatrix.description_matrix):
        for j, val in enumerate(desc):
            worksheet.write(desc_row_start_pos + i, desc_col_start_pos + j, val)
    worksheet.write(i + 2, j, 'Sum')

    # Write row totals
    row_totals_col_start_pos = desc_col_start_pos + j + 1
    row_sums = worklogmatrix.row_sums
    for i in range(worklogmatrix.number_of_rows):
        worksheet.write(desc_row_start_pos + i, row_totals_col_start_pos, row_sums[i])
    worksheet.write(desc_row_start_pos + i + 1, row_totals_col_start_pos, sum(row_sums))

    # Write data
    data_col_start_pos = row_totals_col_start_pos
    for i, data in enumerate(worklogmatrix.data_matrix):
        for j, time in enumerate(data):
            worksheet.write(desc_row_start_pos + i, data_col_start_pos + 1 + j, time)

    # Write column totals
    for i in range(worklogmatrix.number_of_columns):
        start_row_pos = desc_row_start_pos + worklogmatrix.number_of_rows
        start_col_pos = data_col_start_pos + 1 + i
        worksheet.write(start_row_pos, start_col_pos, worklogmatrix.col_sums[i])

    workbook.close()


def merge_data_and_desc(desc_matrix, data_matrix):
    merged_matrix = data_matrix

    for i, el in enumerate(desc_matrix):
        desc_list = list(el)
        merged_matrix[i].insert(0, desc_list[1])
        merged_matrix[i].insert(0, desc_list[0])

    return merged_matrix


def print_csv_data(csv_data, sep=','):
    csv_writer = csv.writer(sys.stdout, delimiter=sep, quoting=csv.QUOTE_NONNUMERIC,
        strict=True, doublequote=False, escapechar='\\')

    for i in range(len(csv_data)):
        csv_writer.writerow(csv_data[i])

def main(server_name, user_name, password):
    """ The main function. Initialize jira extractor, and generate spreadsheet. """

    jira = JiraExtractor(server_name, user_name, password)
    worklog_matrix = WorklogMatrix(jira.extracted_data)
    ##generate_spreadsheet(jira.extracted_data, output_name)

    csv_data = merge_data_and_desc(worklog_matrix.description_matrix, worklog_matrix.data_matrix)
    print_csv_data(csv_data)
    print('Total hours spent:', jira.total_time_in_seconds / 3600)


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
    -o --output output.xlsx
        The output file name. Must end with .xlsx!
  Usage Example:
    $ python jira_worklog_sum.py  -s https://example.jira.com -u username -p password
  """)


if __name__ == '__main__':
    output_name = 'jira-worklog-' + str(date.today()) + '.xlsx'
    server_name = ''
    user_name = ''
    password = ''
    opts, args = [], []

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
