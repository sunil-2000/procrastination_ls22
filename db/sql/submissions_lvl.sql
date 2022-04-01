DROP TABLE IF EXISTS submissions;

CREATE TABLE submissions AS
WITH valid_stu_demographics AS (
  SELECT DISTINCT ON ("anon-netid")
    "anon-netid" AS anon_netid,
    "EFFDT_GENDER" AS gender,
    "ST_ETHNIC_IPEDS" AS ethnicity,
    "ST_URM_FLAG" AS is_a_urm,
    "FIRST_GENERATION" AS first_gen_status
  FROM
    "STU_ENROLLMENT"
),
valid_enrollment AS (
  SELECT DISTINCT ON (user_id,
    course_id)
    id,
    user_id,
    course_id,
    type,
    workflow_state
  FROM
    enrollment_dim
)
SELECT DISTINCT
  sd.id AS submission_id,
  cd.id AS course_id,
  cd.name AS course_name,
  ad.title AS title,
  ad.id AS assignment_id,
  ad.due_at AS due_date,
  sd.submitted_at AS submitted_at,
  sd.grade AS sd_grade,
  sd.attempt AS attempts,
  sd.submission_type,
  ud.id AS user_id,
  sf.score AS score,
  sf.published_score AS published_score,
  ad.points_possible AS points_possible,
  vsd.gender,
  vsd.ethnicity,
  vsd.is_a_urm,
  vsd.first_gen_status,
  csf.current_score,
  csf.final_score,
  ve.id,
  ve.type,
  ve.workflow_state
FROM
  submission_dim sd
  INNER JOIN submission_fact sf ON sf.submission_id = sd.id
  LEFT JOIN assignment_dim ad ON ad.id = sd.assignment_id
  LEFT JOIN course_dim cd ON cd.id = ad.course_id
  LEFT JOIN user_dim ud ON ud.id = sd.user_id
  LEFT JOIN pseudonym_dim pd ON pd.user_id = ud.id
  LEFT JOIN valid_stu_demographics vsd ON vsd.anon_netid = pd.unique_name 
  LEFT JOIN valid_enrollment ve ON ve.user_id = ud.id
    AND ve.course_id = cd.id
  LEFT JOIN course_score_fact csf ON csf.enrollment_id = ve.id
WHERE
  ad.course_id IN (
    SELECT
      course_canvas_id
    FROM
      z_course_meta_filtered_netids
    WHERE
      submissions IS NOT NULL
      AND enrollments IS NOT NULL
      AND assignments IS NOT NULL
      AND assignments > 5
      AND enrollments > 20
      AND submissions > 100)
  AND sd.submission_type IS NOT NULL
  -- AND sd.submission_type = 'online_quiz' -- remove
  AND sd.submitted_at IS NOT NULL
  AND sd.workflow_state != 'unsubmitted'
  AND sd.grade_matches_current_submission
  AND vsd.anon_netid IS NOT NULL
  -- AND cd.sis_source_id IS NOT NULL  -- add this line if rebuilding table (otherwise just left join with course dim using this filter)
ORDER BY
  due_date;