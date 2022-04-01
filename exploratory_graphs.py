from textwrap import wrap
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum
import pandas as pd

# Global Attributes
sns.set_style("whitegrid")
plt.rcParams["xtick.bottom"] = True
plt.rcParams["ytick.left"] = True
plt.rc("axes", edgecolor="black")


class Graphs:
    """
    Exploratory graph methods 
    """
    def student_time_plot(data, save_pdf=False):
        """
        course_id: id of course
        """
        mean_ranks = data.groupby(["user_id"])["assignment_percentile_ranks"].mean()
        student_low = (
            mean_ranks.where(mean_ranks < 0.25).dropna().sample(n=1, random_state=1)
        )
        student_med = (
            mean_ranks.where((mean_ranks < 0.6) & (mean_ranks > 0.4))
            .dropna()
            .sample(n=1, random_state=1)
        )
        student_high = (
            mean_ranks.where(mean_ranks > 0.75).dropna().sample(n=1, random_state=1)
        )

        print(
            "student low: {}, \tstudent median: {}, \tstudent high: {}".format(
                student_low.iloc[0], student_med.iloc[0], student_high.iloc[0]
            )
        )

        low_stud_full = data[data["user_id"] == student_low._index[0]]
        med_stud_full = data[data["user_id"] == student_med._index[0]]
        high_stud_full = data[data["user_id"] == student_high._index[0]]

        print(len(low_stud_full), len(med_stud_full), len(high_stud_full))

        fig = plt.figure(figsize=(16, 5))
        labels = ["student 1", "student 2", "student 3"]
        for f, l in zip([low_stud_full, med_stud_full, high_stud_full], labels):

            f = f.sort_values(by=["due_date"])
            f = f.drop_duplicates(subset=["due_date"])
            assignment_list = ["A" + str(k) for k in list(range(len(f["due_date"])))]

            plt.plot(
                assignment_list, f["assignment_percentile_ranks"], label=l, alpha=0.5
            )
            sns.scatterplot(x=assignment_list, y=f["assignment_percentile_ranks"])

        plt.title("Submission Time Percentile Ranks Within a Course")
        plt.ylabel("Submission Time Percentile Rank", fontsize=24, fontweight="bold")
        plt.xlabel("Assignment", fontsize=24, fontweight="bold")
        plt.legend(
            prop={"size": 20},
            loc="upper center",
            bbox_to_anchor=(0.5, 1.25),
            fancybox=True,
            shadow=True,
            ncol=5,
        )
        plt.xticks(fontsize=16, color="black", rotation=315)
        plt.yticks(fontsize=16, color="black")

        if save_pdf:
            plt.savefig(
                "student_time_plot.pdf", format="pdf", bbox_inches="tight", dpi=200
            )
        plt.show()

    def course_p_score_dist(
        data, course_id_lst, print_meta=False, group_meta_fn=None, save_pdf=False
    ):
        """
        full_data(df) = submission level data of x number of courses
        print_meta(bool): print meta information for each course
        group_meta_fn(function):optional debug function for grouped data at course level
        """
        courses = data.groupby(["course_id", "course_name"], as_index=False)
        plt.figure(figsize=(50, 60))
        n_courses = courses.ngroups
        fig, axes = plt.subplots(
            ncols=3, nrows=n_courses, figsize=(14, 18), sharex=True, sharey=True
        )

        row_index = 0

        for course_iter, ax_row in zip(course_id_lst, axes):

            course, data = course_iter[0], course_iter[1]

            # possible debug function
            if group_meta_fn is not None:
                group_meta_fn(data)

            if print_meta:
                group_meta_fn(data)
            ## Plotting

            if row_index == 0:
                ax_row[0].set_title("Gender")
                ax_row[1].set_title("First Generation")
                ax_row[2].set_title("Ethnicity")

            last_col = False
            if row_index == n_courses - 1:
                # set legends
                last_col = True

            Graphs._gender_plot(data, ax_row, last_col, "procrastination_mean_rank")
            Graphs._fg_plot(data, ax_row, last_col, "procrastination_mean_rank")
            Graphs._ethnicity_plot(
                data, ax_row, course[1], last_col, "procrastination_mean_rank"
            )
            # pass course title because last graph in row

            row_index += 1

        if save_pdf:
            plt.savefig("matrix_density_plots.pdf", format="pdf", bbox_inches="tight")

        plt.show()

    def _gender_plot(data, ax_row, legend, col_name):
        sns.kdeplot(
            data[data["gender"] == "M"][col_name],
            color="lightblue",
            ax=ax_row[0],
            label="Male",
            clip=[0, 1],
        )
        sns.kdeplot(
            data[data["gender"] == "F"][col_name],
            color="pink",
            ax=ax_row[0],
            label="Female",
            clip=[0, 1],
        )
        if legend:
            ax_row[0].legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.3),
                fancybox=True,
                shadow=True,
                ncol=2,
            )

    def _fg_plot(data, ax_row, legend, col_name):
        colors = sns.color_palette("RdYlBu", n_colors=2)
        sns.kdeplot(
            data[data["first_gen_status"] == "Y"][col_name],
            color=colors[0],
            ax=ax_row[1],
            label="Y",
            clip=[0, 1],
        )
        sns.kdeplot(
            data[data["first_gen_status"] == "N"][col_name],
            color=colors[1],
            ax=ax_row[1],
            label="N",
            clip=[0, 1],
        )
        if legend:
            ax_row[1].legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.3),
                fancybox=True,
                shadow=True,
                ncol=2,
            )

    def _ethnicity_plot(data, ax_row, course_name, legend, col_name):
        colors = sns.color_palette("Dark2", n_colors=5)
        sns.kdeplot(
            data[data["ethnicity"] == "White"][col_name],
            color=colors[0],
            ax=ax_row[2],
            label="White",
            clip=[0, 1],
        )
        sns.kdeplot(
            data[data["ethnicity"] == "Asian"][col_name],
            color=colors[1],
            ax=ax_row[2],
            label="Asian",
            clip=[0, 1],
        )
        sns.kdeplot(
            data[data["ethnicity"] == "Black"][col_name],
            color=colors[2],
            ax=ax_row[2],
            label="Black",
            clip=[0, 1],
        )
        sns.kdeplot(
            data[data["ethnicity"] == "Hispanic"][col_name],
            color=colors[3],
            ax=ax_row[2],
            label="Hispanic",
            clip=[0, 1],
        )

        wrapped_name = "\n".join(wrap(course_name, 12))
        text = ax_row[2].text(
            1.4,
            4,
            wrapped_name,
            size=11,
            verticalalignment="center",
            rotation=270,
            wrap=True,
        )

        if legend:
            ax_row[2].legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.3),
                fancybox=True,
                shadow=True,
                ncol=4,
            )


    def _mean_std_count_group(data, group, col_name):
        """
        data(df): dataframe
        group(str): parameter to group df by
        returns [names, means, std, se] of group wrt percentile_rank
        """
        grouped_data = data.groupby(group, as_index=False)[col_name].agg(
            [np.size, np.median, np.std]
        )
        names = list(data.groupby(group).groups)
        means, std, se = (
            list(grouped_data["median"].values),
            list(grouped_data["std"].values),
            list(grouped_data["std"].values / np.sqrt(grouped_data["size"]).values),
        )
        return names, means, std, se


    def se_plot(data, axis, col_name, group):
        """
        generates statistics for each demographic group and plots the data along given axis
        """
        class Group(Enum):
            GENDER = 0
            ETHNICITY = 1
            FG = 2
            ALL = 4

        colors = sns.color_palette("Dark2", n_colors=3)

        if group == Group.ALL:
            filtered_ethnicity_data = data.query(
                "ethnicity == 'Black' | ethnicity == 'White'| ethnicity == 'Asian' | ethnicity == 'Hispanic'"
            )
            print(
                "Filtered {} rows (students not in ethnicity groups)".format(
                    len(data) - len(filtered_ethnicity_data)
                )
            )
            g_names, g_means, g_std, g_se = Graphs._mean_std_count_group(data, "gender", col_name)
            fg_names, fg_means, fg_std, fg_se = Graphs._mean_std_count_group(
                data, "first_gen_status", col_name
            )
            e_names, e_means, e_std, e_se = Graphs._mean_std_count_group(
                filtered_ethnicity_data, "ethnicity", col_name
            )

        if group == Group.GENDER:
            g_names, g_means, g_std, g_se = Graphs._mean_std_count_group(data, "gender", col_name)
            axis.errorbar(
                g_names,
                g_means,
                yerr=g_se,
                fmt=" ",
                label="gender",
                mec="grey",
                markersize=7,
                marker="s",
                mew=1,
                color=colors[0],
            )
            return
        if group == Group.ETHNICITY:
            e_names, e_means, e_std, e_se = Graphs._mean_std_count_group(
                data, "ethnicity", col_name
            )
            axis.errorbar(
                e_names,
                e_means,
                yerr=e_se,
                fmt=" ",
                label="ethnicity",
                mec="grey",
                markersize=7,
                marker="s",
                mew=1,
                color=colors[1],
            )
            return
        if group == Group.FG:
            fg_names, fg_means, fg_std, fg_se = Graphs._mean_std_count_group(
                data, "first_gen_status", col_name
            )
            axis.errorbar(
                fg_names,
                fg_means,
                yerr=fg_se,
                fmt=" ",
                label="first_gen_status",
                mec="grey",
                markersize=7,
                marker="s",
                mew=1,
                color=colors[2],
            )
            return
        axis.errorbar(
            g_names,
            g_means,
            yerr=g_se,
            fmt=" ",
            label="gender",
            mec="grey",
            markersize=7,
            marker="s",
            mew=1,
        )
        axis.errorbar(
            e_names,
            e_means,
            yerr=e_se,
            fmt=" ",
            label="ethnicity",
            mec="grey",
            markersize=7,
            marker="s",
            mew=1,
        )
        axis.errorbar(
            fg_names,
            fg_means,
            yerr=fg_se,
            fmt=" ",
            label="first_gen_status",
            mec="grey",
            markersize=7,
            marker="s",
            mew=1,
        )


    def final_score_box(data):
        """
        final score distribution
        data: submission level data (df)
        """
        data = data[["final_score_percentile_ranks", "course_id"]]
        grade_stats = data.groupby("course_id").agg([np.mean, np.median, np.std])
        sns.boxplot(data=grade_stats)
        plt.show()


    def final_score_dist(data):
        """
        data: submissions level data (df)
        """
        data = data[["final_score_percentile_ranks", "course_id"]]
        grade_stats = data.groupby("course_id").agg([np.mean, np.median, np.std])
        sns.histplot(data=grade_stats["final_score_percentile_ranks", "mean"])
        plt.show()

    def validate_n_stud_assign(data):
        """
        data: submission level data (df)
        """
        data = data[['course_id', 'assignment_id', 'user_id']]
        stud_data = data.groupby("course_id")["user_id"].nunique()
        assign_data = data.groupby("course_id")["assignment_id"].nunique()
        data = data.merge(assign_data, on=["course_id"], how="left")
        data = data.rename(
            columns={
                "assignment_id_x": "assignment_id",
                "assignment_id_y": "n_assignments",
            }
        )
        data = data.merge(stud_data, on=["course_id"], how="left")
        data = data.rename(columns={"user_id_x": "user_id", "user_id_y": "n_students"})
        student_course = data.groupby(['course_id'], as_index=False).head(1).copy()
        
        student_course = student_course[['course_id', 'n_assignments', 'n_students']]
        student_counts = student_course.sort_values(by=['n_students'])
        assignment_counts = student_course.sort_values(by=['n_assignments'])

        print(len(student_course))
        print(len(student_counts[student_counts['n_students'] < 20]))
        print(len(assignment_counts[assignment_counts['n_assignments'] < 5]))
