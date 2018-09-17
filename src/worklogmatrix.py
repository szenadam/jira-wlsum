from itertools import groupby
from operator import itemgetter
from natsort import natsorted


class WorklogMatrix:
    def __init__(self, extracted_data):
        self.data_matrix = self.create_calendar_data_matrix(extracted_data)
        self.description_matrix = self.create_description_matrix(extracted_data)
        self.row_sums = self.get_rows_sum(self.data_matrix)
        self.col_sums = self.get_columns_sum(self.data_matrix)
        self.rows_len = len(extracted_data)
        self.cols_len = len(extracted_data[0])


    def get_uniq_keys(self, data):
        """ Create list of unique issue keys from the data. """
        uniq = []
        l = list({v['issueKey']: v for v in data}.values())
        for d in l:
            uniq.append(d['issueKey'])
        return uniq


    def sum_up_worklog_for_a_day(self, data):
        """ Key function for aggregating the time spent in an issue a day. """
        grouper = itemgetter("issueKey", "dayStarted")
        result = []
        for key, grp in groupby(sorted(data, key=grouper), grouper):
            temp_dict = dict(zip(["issueKey", "dayStarted"], key))
            temp_dict["timeSpentSeconds"] = sum(item["timeSpentSeconds"] for item in grp)
            result.append(temp_dict)
        return result

    def create_calendar_data_matrix(self, data):
        """ Create the calendar data matrix from an extracted worklog list.
          TODO: Needs to be simplified later for readability, modularity, etc.
        """
        number_of_rows = len(data) ### BUG: we need the number of unique jira tickets
        number_of_columns = len(data[0]) ### BUG: the nummber of days
        calendar_matrix = [[0 for x in range(number_of_columns)] for y in range(number_of_rows)]
        summed_up_data = self.sum_up_worklog_for_a_day(data)
        sorted_data = natsorted(summed_up_data, key=lambda k: k['issueKey'])
        uniq_keys = self.get_uniq_keys(sorted_data)

        for i, key in enumerate(uniq_keys):
            for worklog in sorted_data:
                if worklog['issueKey'] == key:
                    calendar_matrix[int(i)][int(worklog['dayStarted'] - 1)] = round(worklog['timeSpentSeconds'] / 3600, 2)

        return calendar_matrix

    def convert_seconds_to_hours(self, data_matrix):
        """ Convert seconds to hours """
        for i, data in enumerate(data_matrix):
            for j, time in enumerate(data):
                data_matrix[i][j] = round(time / 3600, 2)
        return data_matrix

    def get_columns_sum(self, data_matrix):
        """ Sum up columns in a 2D data matrix """
        col_sums = []
        zipped = zip(*data_matrix)
        for d in zipped:
            col_sums.append(sum(d))
        return col_sums

    def get_rows_sum(self, data_matrix):
        """ Sum up rows in a 2D data matrix """
        row_sums = []
        for i in range(len(data_matrix)):
            s = sum(data_matrix[i])
            row_sums.append(s)
        return row_sums

    def create_description_matrix(self, extracted_data):
        description = []
        for data in extracted_data:
            description.append(tuple((data.key, data.summary)))
        return description
