import pandas as pd
import pandas.api.types as ptypes
import sys
import math 


class SubmissionData:
    def __init__(self, columns, file, a_n=5, s_n=20, a_thres=0.5, s_thres=0.5, full_clean=True):
        """
        a_n (int > 0): assignment number invariant
        s_n (int > 0): student number invariant 
        a_thres (float): assignment filter threshold [0..1]
        s_thress (float): student filter threshold [0..1]
        """
        self.a_n, self.s_n = a_n, s_n
        self.a_thres, self.s_thres = a_thres, s_thres

        self.data = pd.read_csv(file, usecols=columns, low_memory=False)
        print("size of df: {} mb".format(sys.getsizeof(self.data) / 1e6))
        self.student_course_lvl = None 

        if full_clean:
            og = self.data.groupby(['course_id', 'user_id']).ngroups
            og_c = self.data.groupby(['course_id']).ngroups
            print('og student course obs: {}'.format(og))
            print('og course obs: {}'.format(og_c))
            self.datetime_conversions()
            self.ethnicity_remap()

            self.aggegate_class_stats_join()
            self.course_filter()
            self.assignment_filter()
            self.student_filter()
            
            self.validate_n_stud_assign()
            self.add_ranks()
            self.group_by_students()

            self.student_course_lvl.dropna() # pd.rank ignores nan values --> sets them to nan



    def assignment_filter(self):
        total = self.data.groupby(['course_id', 'user_id']).ngroups
        total_c = self.data.groupby(['course_id']).ngroups
        print('assignment filter student_course obs (prior): {}'.format(total))
        print('assignment filter course obs (prior): {}'.format(total_c))
        assignment_filter = lambda df: (df['user_id'].nunique() / df.head(1)["course_size"].values[0]) > self.a_thres
        
        self.data = self.data.groupby("assignment_id").filter(assignment_filter)

        excluded = self.data.groupby(['course_id', 'user_id']).ngroups
        excluded_c = self.data.groupby(['course_id']).ngroups
        
        print('assignment filter student-course obs (after): {}, num excluded: {}'.format(excluded, total-excluded))
        print('assignment filter course obs (after): {}, num excluded: {}'.format(excluded_c, total_c - excluded_c))

    def course_filter(self):
        total = self.data.groupby(['course_id', 'user_id']).ngroups
        total_c = self.data.groupby(['course_id']).ngroups
        print('course filter student_course obs (prior): {}'.format(total))
        print('course filter course obs (prior): {}'.format(total_c))
        course_filter = (
            lambda df: df.head(1)["course_mean"].values[0] != 0
        )  # course_mean constant with course groupby
        self.data = self.data.groupby("course_id").filter(course_filter)
        
        excluded = self.data.groupby(['course_id', 'user_id']).ngroups
        excluded_c = self.data.groupby(['course_id']).ngroups
        print('course filter student-course obs (after): {}, num excluded: {}'.format(excluded, total-excluded))
        print('course filter course obs (after): {}, num excluded: {}'.format(excluded_c, total_c - excluded_c))

    def student_filter(self):
        total = self.data.groupby(['course_id', 'user_id']).ngroups
        total_c = self.data.groupby(['course_id']).ngroups
        print('student filter student_course obs (prior): {}'.format(total))
        print('student filter course obs (prior): {}'.format(total_c))
        n_assignments = self.data.groupby("course_id")["assignment_id"].nunique()
        self.data = self.data.merge(n_assignments, on=["course_id"], how="left")
        self.data = self.data.rename(
            columns={
                "assignment_id_x": "assignment_id",
                "assignment_id_y": "n_assignments",
            }
        )
        student_filter = (
            lambda df: df["assignment_id"].nunique() > math.floor(df["n_assignments"].head(1) * self.s_thres)
        )

        self.data = self.data.groupby(["user_id", "course_id"]).filter(student_filter)
        excluded = self.data.groupby(['course_id', 'user_id']).ngroups
        excluded_c = self.data.groupby(['course_id']).ngroups
        print('student filter student-course obs (after): {}, num excluded: {}'.format(excluded, total-excluded))
        print('student filter course obs (after): {}, num excluded: {}'.format(excluded_c, total_c - excluded_c))


    def datetime_conversions(self):
        self.data["submitted_at"] = pd.to_datetime(self.data["submitted_at"])
        self.data["due_date"] = pd.to_datetime(self.data["due_date"])
        # grade_matches_current_submission in sd field gurantees submissions are the most recent wrt assignment

    def aggegate_class_stats_join(self):
        # course sizes and means
        course_sizes = self.data.groupby("course_id")["user_id"].nunique()
        course_means = self.data.groupby("course_id")["final_score"].mean()

        # course meta merges
        self.data = self.data.merge(course_sizes, on="course_id", how="left")
        self.data = self.data.rename(
            columns={"user_id_x": "user_id", "user_id_y": "course_size"}
        )
        print("class size joined")
        self.data = self.data.merge(course_means, on="course_id", how="left")
        self.data = self.data.rename(
            columns={"final_score_x": "final_score", "final_score_y": "course_mean"}
        )
        print("class mean joined")

    def add_ranks(self):
        # Submissions Ranks
        assert ptypes.is_datetime64_any_dtype(self.data["submitted_at"])

        self.data["assignment_ranks"] = self.data.groupby("assignment_id")[
            "submitted_at"
        ].rank(
            method="average"
        )  # take average rank to break ties
        self.data["assignment_percentile_ranks"] = self.data.groupby("assignment_id")[
            "submitted_at"
        ].rank(method="average", pct=True)
        print("ranks added")
        # mean assignment ranks (student, course level)
        mean_ranks = self.data.groupby(["user_id", "course_id"])[
            "assignment_ranks"
        ].mean()
        median_percentile_ranks = self.data.groupby(["user_id", "course_id"])[
            "assignment_percentile_ranks"
        ].median()
        var_percentile_ranks = self.data.groupby(["user_id", "course_id"])[
            "assignment_percentile_ranks"
        ].var()
        std_percentile_ranks = self.data.groupby(["user_id", "course_id"])[
            "assignment_percentile_ranks"
        ].std()
        mean_percentile_ranks = self.data.groupby(["user_id", "course_id"])[
            "assignment_percentile_ranks"
        ].mean()
        print("mean ranks computed")
        # rank merge
        self.data = self.data.merge(mean_ranks, on=["user_id", "course_id"], how="left")

        self.data = self.data.rename(
            columns={
                "assignment_ranks_x": "assignment_ranks",
                "assignment_ranks_y": "mean rank",
            }
        )

        self.data = self.data.merge(
            mean_percentile_ranks, on=["user_id", "course_id"], how="left"
        )

        self.data = self.data.rename(
            columns={
                "assignment_percentile_ranks_x": "assignment_percentile_ranks",
                "assignment_percentile_ranks_y": "procrastination_mean_rank",
            }
        )

        self.data = self.data.merge(
            median_percentile_ranks, on=["user_id", "course_id"], how="left"
        )
        self.data = self.data.rename(
            columns={
                "assignment_percentile_ranks_x": "assignment_percentile_ranks",
                "assignment_percentile_ranks_y": "procrastination_median_rank",
            }
        )

        self.data = self.data.merge(
            var_percentile_ranks, on=["user_id", "course_id"], how="left"
        )
        self.data = self.data.rename(
            columns={
                "assignment_percentile_ranks_x": "assignment_percentile_ranks",
                "assignment_percentile_ranks_y": "procrastination_var_rank",
            }
        )

        self.data = self.data.merge(
            std_percentile_ranks, on=["user_id", "course_id"], how="left"
        )
        self.data = self.data.rename(
            columns={
                "assignment_percentile_ranks_x": "assignment_percentile_ranks",
                "assignment_percentile_ranks_y": "procrastination_std_rank",
            }
        )

        print("mean ranks merged")

    def ethnicity_remap(self):
      self.data['ethnicity'] = self.data['ethnicity'].replace('Non Resident Alien', 'International')
      self.data['ethnicity'] = self.data['ethnicity'].replace('Two or More Races', 'Multiple Races')
      self.data['ethnicity'] = self.data['ethnicity'].replace('Hawaii/Pac', 'Native/Pacific')
      self.data['ethnicity'] = self.data['ethnicity'].replace('Am. Indian', 'Native/Pacific')
      self.data['ethnicity'] = self.data['ethnicity'].replace('No Citizenship Status', 'Unknown')

    def group_by_students(self):
      # keep only unique course_id, user_id (student level)
      # as_index=False --> treat user_id,course_id group as new index
      self.student_course_lvl = self.data.groupby(['user_id', 'course_id'], as_index=False).head(1).copy()

      # final grade ranks
      self.student_course_lvl['final_score_ranks'] = self.student_course_lvl.groupby('course_id')['final_score'].rank(method='average')
      self.student_course_lvl['final_score_percentile_ranks'] = self.student_course_lvl.groupby('course_id')['final_score'].rank(method='average', pct=True)
      print('final score ranks added')

      # drop unnecessary submission-related columns (non-aggregate columns)
      self.student_course_lvl = self.student_course_lvl.drop(['submitted_at', 'due_date', 'assignment_id',
                                          'assignment_ranks', 'assignment_percentile_ranks'], axis=1)
      print('dropped submission/assignment related columns')

      print('df rows (student-course level):{}'.format(len(self.student_course_lvl)))

    def validate_n_stud_assign(self):
        print('validating student and assignment count invariants')
        print('submissions observations after all filter methods: {}'.format(len(self.data)))
        stud_data = self.data.groupby("course_id")["user_id"].nunique()
        assign_data = self.data.groupby("course_id")["assignment_id"].nunique()
        
        self.data = self.data.merge(assign_data, on=["course_id"], how="left")
        self.data = self.data.rename(
            columns={
                "assignment_id_x": "assignment_id",
                "assignment_id_y": "n_assignments_updated",
            }
        )
        self.data = self.data.merge(stud_data, on=["course_id"], how="left")
        self.data = self.data.rename(columns={"user_id_x": "user_id", "user_id_y": "n_students_updated"})

        student_invariant = lambda df: df.head(1)["n_students_updated"].values[0] > self.s_n
        assignment_invariant = lambda df: df.head(1)["n_assignments_updated"].values[0] > self.a_n

        self.data = self.data.groupby(['course_id']).filter(student_invariant)
        self.data = self.data.groupby(['course_id']).filter(assignment_invariant)

        print('final submissions obs (maintaining invariants): {}'.format(len(self.data)))
