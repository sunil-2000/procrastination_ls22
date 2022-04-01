-- generate meta information for every course

DROP VIEW IF EXISTS course_meta_submissions;


CREATE VIEW course_meta_submissions AS WITH valid_stu_demographics AS
  ( SELECT DISTINCT ON ("anon-netid") "anon-netid" AS anon_netid,
                       "EFFDT_GENDER" AS gender,
                       "ST_ETHNIC_IPEDS" AS ethnicity,
                       "ST_URM_FLAG" AS is_a_urm,
                       "FIRST_GENERATION" AS first_gen_status
   FROM "STU_ENROLLMENT")
SELECT cd.id AS course_canvas_id,
       cd.name AS course_name,
       cd.code AS course_code,
       cd.start_at AS strt_date,
       cd.root_account_id,
       cd.account_id,
       cd.workflow_state,
       COUNT(DISTINCT sd.id) AS submissions
FROM submission_dim sd
INNER JOIN submission_fact sf ON sf.submission_id = sd.id
LEFT JOIN course_dim cd ON cd.id = sf.course_id
LEFT JOIN user_dim ud ON ud.id = sf.user_id
LEFT JOIN pseudonym_dim pd ON pd.user_id = ud.id
LEFT JOIN valid_stu_demographics vsd ON vsd.anon_netid = pd.unique_name
WHERE sd.grade_matches_current_submission
  AND sd.submitted_at IS NOT NULL
  AND sd.workflow_state != 'unsubmitted'
  AND sd.submission_type IS NOT NULL
  AND vsd.anon_netid IS NOT NULL
GROUP BY course_canvas_id,
         course_name,
         course_code,
         strt_date
ORDER BY submissions DESC;

