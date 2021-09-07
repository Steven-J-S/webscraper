-- maak overzicht met de url's uit BRIN.

select distinct nr_administratie
     , to_char(DT_BEGIN_RECORD, 'yyyymmdd') as DT_BEGIN_RECORD
     , to_char(DT_EINDE_RECORD, 'yyyymmdd') as DT_EINDE_RECORD
     , CODE_FUNCTIE  
     , CODE_SOORT                           
     , INTERNET as URL
  from DRI.DRI_ORGANISATIES
 where internet is not null
   AND (CODE_STAND_RECORD = 'A' OR CODE_STAND_RECORD = 'H')
ORDER BY 1

-- sla op als org_url_20180730.tsv
