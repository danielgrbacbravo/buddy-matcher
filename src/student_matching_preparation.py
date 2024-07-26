import pandas as pd


def add_matches_column(self):
    if 'Matches' not in self.local_students_copy:
        capacity_index = self.local_students_copy.columns.get_loc('Capacity')
        try:
            self.local_students_original.insert(capacity_index + 2, 'Matches',
                                                [0] * len(self.local_students_original))
            self.local_students_copy.insert(capacity_index + 2, 'Matches', [0] * len(self.local_students_copy))
        except IndexError:
            print(f"Error Creating 'Matches' Column in Local Students DataFrame")
            exit()


def add_id_and_adjust_capacity(self):
    self.local_students_copy.insert(0, 'id', range(0, len(self.local_students_copy)))
    self.local_students_copy = self.local_students_copy.loc[
        self.local_students_copy.index.repeat(self.local_students_copy.Capacity)].assign(Capacity=1, Extra='No')



def handle_extra_buddies(self):
    if self.base_local_capacity < self.base_necessity:
        print(f"Extra Students Needed")
        additional_local_students = self.local_students_copy.loc[
            self.local_students_copy['ExtraBuddy'] == 'Yes'].assign(Capacity=0)
        self.local_students_copy = pd.concat([self.local_students_copy, additional_local_students],
                                             ignore_index=True,
                                             axis=0).sort_values('id').reset_index(drop=True)
    else:
        self.local_students_copy = self.local_students_copy.sort_values('id').reset_index(drop=True)



def _prepare_for_one_to_one_matching(self):
    self.add_matches_column()
    self.add_id_and_adjust_capacity()
    self.handle_extra_buddies()
