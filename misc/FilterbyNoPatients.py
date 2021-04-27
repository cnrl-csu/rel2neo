import pandas as pd
import numpy as np

class FilterByNoPatients:

    def __init__(self):
        self.no_of_patients = 100
        self.patients_ids = []
        self.file_path = "F:\MIMIC\mimic-iii-clinical-database-1.4\CSV_FILES"

    def read_write(self):
        patients_df = pd.read_csv(self.file_path+'\PATIENTS.csv', nrows=self.no_of_patients)
        self.patients_ids = patients_df['SUBJECT_ID'].tolist()
        patients_df.to_csv(self.file_path + '\PATIENTS_' + str(self.no_of_patients) + '.csv', index=False)

        file_names = ['ADMISSIONS','DRGCODES','ICUSTAYS','PRESCRIPTIONS_ADMIT','PRESCRIPTIONS_ICUSTAY', 'SERVICES']

        for file_name in file_names:
            df = pd.read_csv(self.file_path+'\\'+file_name+'.csv').replace(np.nan, '', regex=True)
            df = df[df['SUBJECT_ID'].isin(self.patients_ids)]
            df.to_csv(self.file_path+'\\'+file_name+'_'+str(self.no_of_patients)+'.csv', index=False)

if __name__ == "__main__":
    f = FilterByNoPatients()
    f.read_write()