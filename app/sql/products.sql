WITH projects_products AS (

  SELECT 
    TRIM(projekty.nr_wlasny) AS "project_number",
    TRIM(REGEXP_REPLACE(indeksy.nazwa_indeksu, '^:product_prefix', '')) AS "product_symbol"

  FROM 
    g.mzk_zamow_klienta as zamowienia
  left join
    g.mzk_zamow_klienta_pozycje as pozycje
      on zamowienia.rok = pozycje.rok_zamowienia 
      and zamowienia.nr = pozycje.nr_zamowienia
  left join
    g.gm_indeksy as indeksy
      on indeksy.id_indeksu = pozycje.id_materialu
  left join
    g.mzk_projekty_zwiazki as zwiazki
      on zwiazki.rodzaj_zrodla = 3
      and zwiazki.id_zrodla1 = zamowienia.rok
      and zwiazki.id_zrodla2 = zamowienia.nr
  left join 
    g.mzk_projekty as projekty 
      on projekty.nr = zwiazki.nr_projektu 
      and projekty.rok = zwiazki.rok_projektu

  WHERE
    TRIM(projekty.nr_wlasny) in (:project_numbers)
  and
    exists (
      SELECT 1
      FROM unnest(array[:product_labels]) AS pattern
      WHERE TRIM(indeksy.nazwa_indeksu) ILIKE pattern)
  and
    indeksy.nazwa_indeksu NOT SIMILAR TO '% [[:lower:]]{5,}%'
)

SELECT 
  project_number, 
  ARRAY_AGG(DISTINCT product_symbol)
FROM 
  projects_products 
GROUP BY 
  project_number
;
