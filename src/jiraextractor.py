from jira import JIRA
from datetime import datetime, date
from dateutil.tz import tzlocal
import dateutil.parser
import pytz

class JiraExtractor():
  def __init__(self, server, username, password):
    self.server = server
    self.username = username
    self.password = password
    self.jira = JIRA(self.server, basic_auth=(self.username, self.password))
    self.logged_issues = self.query_logged_issues()
    self.worklogs = self.get_all_worklogs_for_issues(self.logged_issues)
    self.extracted_data = self.extract_data_from_worklogs(self.worklogs)
    self.total_time_in_seconds = self.get_worklogs_total_seconds(self.extracted_data)
    self.number_of_issues = len(self.logged_issues)
    self.last_day = self.get_last_worklog_day(self.extracted_data)


  def query_logged_issues(self):
    """ Query the issues where worklogs were made by the currently logged in user
      TODO: Later should handle dates if teh user is interested in a different time range.
    """
    logged_issues = self.jira.search_issues('worklogAuthor = currentUser() AND worklogDate >= startOfMonth() ORDER BY key ASC')
    return logged_issues


  def is_in_this_month(self, time_created):
    """ Need to check each worklog, otherwise it would sum every time spent for the
    current user. Hopefully the worklog.created is in UTC0. """

    created = dateutil.parser.parse(time_created)
    today = datetime.today()
    if created > datetime(today.year,today.month,1,0,0,0,0,pytz.UTC):
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


  def extract_data_from_worklogs(self, worklogs):
    """ Extract only the necessary attribues from the worklog objects. """
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


  def get_last_worklog_day(self, data):
    """ Last day that has a worklog. Used for the calendar matrix width. """
    last_day = 0
    for d in data:
      if d['dayStarted'] > last_day:
        last_day = d['dayStarted']
    return last_day

  def get_worklogs_total_seconds(self, data):
    """ Sum up all the time spent. """
    total = 0
    for d in data:
      total += d['timeSpentSeconds']
    return total
