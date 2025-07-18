SELECT
    projects.year::text AS "year",
    TRIM(groups.description) AS "group",
    TRIM(projects.own_number) AS "number",
    TRIM(projects.description) AS "partner"
FROM
    g.projects AS projects
    JOIN g.project_groups AS groups ON groups.id = projects.group_id
WHERE
    projects.own_number LIKE '510-%'
    AND TRIM(groups.description) IN (:project_groups)
    AND datasql(projects.date_id) > :since_date::date;
