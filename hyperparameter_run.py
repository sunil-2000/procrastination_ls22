from clean.clean_data import SubmissionData
import statsmodels.formula.api as smf
import numpy as np

data_file = './data/full_data_updated.csv'
columns = ['submitted_at', 'due_date', 'course_id', 'course_name', 'user_id', 'assignment_id',
            'final_score', 'ethnicity', 'gender', 'is_a_urm', 'first_gen_status']

first = True
def dump_results(res, a_n, s_n, a_thres, s_thres):
  with open('ols_coeffs1.txt', 'a') as fh:
    fh.write("\na_n:{}, s_n:{}, a_thres:{}, s_thres{}\n".format(a_n, s_n, a_thres, s_thres))
    fh.write(res.summary().as_text())
  
  with open('ols_coeffs1.csv', 'a', newline="") as c:
    coeffs = res.params.values
    varnames = np.array([key for key, v in res.params.iteritems()])

    if first:
      # write header
      header = np.array(['a_n', 's_n', 'a_thres', 's_thres'])
      header = np.concatenate((header, varnames))
      np.savetxt(c, [header], delimiter=',', fmt='%s')
    
    hyperparameters = np.array([a_n, s_n, a_thres, s_thres])
    data = np.concatenate((hyperparameters, coeffs))
    np.savetxt(c, [data], delimiter=',', fmt='%s')
  
  with open('ols_pvalues1.csv', 'a', newline="") as c1:
    p_values = res.pvalues.round(4).values
    varnames = np.array([key for key, v in res.pvalues.iteritems()])

    if first:
      # write header
      header = np.array(['a_n', 's_n', 'a_thres', 's_thres'])
      header = np.concatenate((header, varnames))
      np.savetxt(c1, [header], delimiter=',', fmt='%s')
    
    hyperparameters = np.array([a_n, s_n, a_thres, s_thres])
    data = np.concatenate((hyperparameters, p_values))
    np.savetxt(c1, [data], delimiter=',', fmt='%s')

  with open('ols_confint1.csv', 'a', newline="") as c2:
    ci_errs = res.conf_int()[0] # 95% ci  = res.pvalues.round(4).values
    varnames = ci_errs.index.values

    if first:
      # write header
      header = np.array(['a_n', 's_n', 'a_thres', 's_thres'])
      header = np.concatenate((header, varnames))
      np.savetxt(c2, [header], delimiter=',', fmt='%s')
    
    hyperparameters = np.array([a_n, s_n, a_thres, s_thres])
    data = np.concatenate((hyperparameters, ci_errs))
    np.savetxt(c2, [data], delimiter=',', fmt='%s')
# OLS(...).fit(cov_type='cluster', cov_kwds={'groups': df['course_id']})
# 3*4*3*3
for a_n in range(5,30,10):
  for s_n in range(10, 50, 10):
    for a_thres in range(1, 4):
      a_thres = a_thres/4
      for s_thres in range(1,4):
        # testing 0.25, 0.5, 0.75
        s_thres = s_thres/4
        dataObj = SubmissionData(columns=columns, file=data_file, full_clean=True, a_n=a_n, s_n=s_n, a_thres=a_thres, s_thres=s_thres)
        print('executing(a_n:{},s_n{},a_thres:{}, s_thres:{}'.format(a_n, s_n,a_thres,s_thres))
        model = smf.ols(formula="procrastination_mean_rank ~ C(gender) + C(is_a_urm) + C(first_gen_status) +C(ethnicity)", data=dataObj.student_course_lvl)
        res = model.fit(cov_type='cluster', cov_kwds={'groups': dataObj.student_course_lvl['course_id']})
        dump_results(res, a_n, s_n, a_thres, s_thres)
        print('done')
        first = False 


