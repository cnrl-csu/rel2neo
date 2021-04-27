import pandas as pd
import numpy as np

class Preprocess:

    def __init__(self):
        self.df = None

    def read_write(self):
        self.df = pd.read_csv('F:\MIMIC\mimic-iii-clinical-database-1.4\CSV_FILES\PRESCRIPTIONS.csv')
        self.df = self.df.replace(np.nan, '', regex=True)

        admit_pres = self.df[self.df['ICUSTAY_ID'] == '']
        icu_pres = self.df[self.df['ICUSTAY_ID'] != '']

        admit_pres.to_csv('F:\MIMIC\mimic-iii-clinical-database-1.4\CSV_FILES\PRESCRIPTIONS_ADMIT.csv', index=False)
        icu_pres.to_csv('F:\MIMIC\mimic-iii-clinical-database-1.4\CSV_FILES\PRESCRIPTIONS_ICUSTAY.csv', index=False)

if __name__=="__main__":
    p = Preprocess()
    p.read_write()