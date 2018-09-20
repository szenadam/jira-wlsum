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
import sys
import xlsxwriter
import getopt


def generate_spreadsheet(extracted_data, workbook_name='worklog.xlsx', start_row=0, start_col=0):
    """ Generate spreadsheet from data matrix """
    workbook = xlsxwriter.Workbook(workbook_name)
    worksheet = workbook.add_worksheet()

    worklogmatrix = WorklogMatrix(extracted_data)

    # Write key and summary
    desc_col_start_pos = start_col
    for i, desc in enumerate(worklogmatrix.description_matrix):
        for j, val in enumerate(desc):
            worksheet.write(start_row + i, desc_col_start_pos + j, val)
    worksheet.write(i + 1, j, "Sum")

    # Write row totals
    row_totals_col_start_pos = desc_col_start_pos + j + 1
    row_sums = worklogmatrix.row_sums
    for i in range(worklogmatrix.number_of_rows):
        worksheet.write(start_row + i, row_totals_col_start_pos, row_sums[i])
    worksheet.write(start_row + i + 1, row_totals_col_start_pos, sum(row_sums))

    # Write data
    data_col_start_pos = row_totals_col_start_pos
    for i, data in enumerate(worklogmatrix.data_matrix):
        for j, time in enumerate(data):
            worksheet.write(start_row + i, data_col_start_pos + 1 + j, time)

    # Write column totals
    for i in range(worklogmatrix.number_of_columns):
        worksheet.write(start_row + worklogmatrix.number_of_rows, data_col_start_pos + 1 + i, worklogmatrix.col_sums[i])

    workbook.close()


def main(server_name, user_name, password):
    """ The main function. Initialize jira extractor, and generate spreadsheet. """

    jira = JiraExtractor(server_name, user_name, password)
    generate_spreadsheet(jira.extracted_data, output_name)

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
