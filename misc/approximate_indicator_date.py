import pandas as pd
import math
import datetime

class ApproximateDates:

    def __init__(self):
        self.df = None

    def read_file(self):
        self.df = pd.read_csv('F:/WJP/data_files/v3/indicator_links.csv')

    def approximate(self):
        for index, row in self.df.iterrows():
            date = row['date']
            if isinstance(date, float) and math.isnan(date) :
                if not isinstance(row['begin_range'], float) :
                    begin = datetime.datetime.strptime(row['begin_range'], '%m/%d/%Y')
                    end = datetime.datetime.strptime(row['end_range'], '%m/%d/%Y')
                    mid = begin + (end - begin)/2
                    mid_date_str = mid.strftime('%m/%d/%Y')
                    print(mid_date_str)
                    self.df.loc[index, ['date']] = mid_date_str

    def write_file(self):
        self.df.to_csv('F:/WJP/data_files/v3/indicator_links_a.csv', index=False)


if __name__=="__main__":
    a = ApproximateDates()
    a.read_file()
    a.approximate()
    a.write_file()