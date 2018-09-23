from jira import JIRA
from datetime import datetime, date
from dateutil.tz import tzlocal
import dateutil.parser
import pytz


class JiraExtractor():
    def __init__(self, server, username, password, for_user, from_date, to_date):
        self.jira = JIRA(server, basic_auth=(username, password))
        self.extracted_data = self.extract_data_from_worklogs(for_user, from_date, to_date)
        self.total_time_in_seconds = self.get_worklogs_total_seconds(self.extracted_data)

    def check_dates(self, from_date, to_date):
        if from_date != 'startOfMonth()':
            vals = list(map(int, from_date.split('-')))
            try:
                date(vals[0], vals[1], vals[2])
            except IndexError as e:
                print(e)
                exit(1)

        if to_date != 'now()':
            vals = list(map(int, from_date.split('-')))
            try:
                date(vals[0], vals[1], vals[2])
            except IndexError as e:
                print(e)
                exit(1)

    def query_logged_issues(self, for_user='currentUser()', from_date='startOfMonth()', to_date='now()'):
        """ Query the issues where worklogs were made by the given user in the given
        time interval. Default is currentUser() and from the start of month until now.
        """

        self.check_dates(from_date, to_date)

        qs_user = f'worklogAuthor = {for_user} AND '
        qs_from_date = f'worklogDate >= {from_date} AND '
        qs_to_date = f'worklogDate <= {to_date} '
        qs_order = f'ORDER BY key ASC'

        logged_issues = self.jira.search_issues(qs_user + qs_from_date + qs_to_date + qs_order)
        return logged_issues

    def is_in_this_month(self, time_created):
        """ Need to check each worklog, otherwise it would sum every time spent for the
        current user. Hopefully the worklog.created is in UTC0. """

        created = dateutil.parser.parse(time_created)
        today = datetime.today()
        if created > datetime(today.year, today.month, 1, 0, 0, 0, 0, pytz.UTC):
            return True
        else:
            return False

    def get_all_worklogs_for_issues(self, issues):
        """ Extract all worklog objects into a list. Add issue key to the worklog object. """
        worklogs = []
        for issue in issues:
            for worklog in self.jira.worklogs(issue.key):
                if self.is_in_this_month(worklog.started):
                    worklog.key = issue.key
                    worklog.summary = issue.fields.summary
                    worklogs.append(worklog)
        return worklogs

    def extract_data_from_worklogs(self, for_user, from_date, to_date):
        """ Extract only the necessary attribues from the worklog objects. """
        logged_issues = self.query_logged_issues(for_user, from_date, to_date)
        worklogs = self.get_all_worklogs_for_issues(logged_issues)
        data = []
        for worklog in worklogs:
            d = {}
            d['issueKey'] = worklog.key
            d['summary'] = worklog.summary
            # The results should be in the local timezone. JIRA stores it in UTC0
            d['dayStarted'] = dateutil.parser.parse(worklog.started).astimezone(tzlocal()).day
            d['timeSpentSeconds'] = worklog.timeSpentSeconds
            data.append(d)
        return data

    def get_worklogs_total_seconds(self, data):
        """ Sum up all the time spent. """
        total = 0
        for d in data:
            total += d['timeSpentSeconds']
        return total
