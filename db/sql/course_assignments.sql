-- generate meta information for every course

DROP VIEW IF EXISTS course_meta_assignments;


CREATE VIEW course_meta_assignments AS
SELECT cd.id as course_canvas_id,
       cd.name as course_name,
       cd.code as course_code,
       cd.start_at AS strt_date,
       cd.root_account_id,
       cd.account_id,
       cd.workflow_state,
       COUNT(DISTINCT ad.id) AS assignments
FROM assignment_dim ad
LEFT JOIN course_dim cd ON cd.id = ad.course_id
WHERE ad.submission_types != 'none' -- none type for iclickers
  AND ad.grading_type != 'not_graded' -- remove
  AND ad.workflow_state = 'published'
GROUP BY course_canvas_id
ORDER BY assignments DESC;

