select
    projekty.rok::text as "year",
    TRIM(grupy.opis) as "group",
    TRIM(projekty.nr_wlasny) as "number",
    TRIM(projekty.opis) as "partner"
from
    g.mzk_projekty as projekty
    join g.mzk_pojekty_grupy as grupy on grupy.id = projekty.id_grupy1
where
    projekty.nr_wlasny like '510-%'
    and TRIM(grupy.opis) IN (:project_groups)
    and datasql(projekty.id_data) > :since_date::date
;


