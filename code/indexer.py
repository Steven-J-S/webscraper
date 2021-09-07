from scraper_utils import *

def indexer():  
  # Laad data
  orgs = 'I:\Team Data-Science\Projecten\webscraper\data\org_url_20210511.txt'
  orgs_df = pd.read_csv(orgs, delimiter = "\t")
  urls_nr = orgs_df[['NR_ADMINISTRATIE', 'URL']][orgs_df['CODE_SOORT']=='BAS'].drop_duplicates(subset='URL').values

  # Maak variables
  exceptions = set()
  exc_path = 'C:\\Users\\ad010sup\\Documents\\schooldocumenten\\exceptions\\'
  ind_path = 'C:\\Users\\ad010sup\\Documents\\schooldocumenten\\index\\'
  max_depth = 2
  count = 0

  for nr, url in urls_nr:
    count += 1
    print(f'Checking:  {nr}  {url}, {count} of {len(urls_nr)}')
    if not os.path.isfile(ind_path+nr+'.pkl'):
      try:
        print('Indexing ...')
        #index = func_timeout(180, index_url, args=(url, 2))
        url = fix_url(url)
        b_url = beautify_url(url)
        b_url = get_url(b_url)
        index = index_url(b_url, max_depth)
      except:
        print('Failed to index ...')
        exceptions.add(b_url)
        with open(exc_path+'index_exceptions.pkl', 'wb') as f:
          pickle.dump(exceptions, f, protocol=pickle.HIGHEST_PROTOCOL)
        continue

      with open(ind_path+f'{nr}.pkl', 'wb') as f:
        pickle.dump(index, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
  indexer()
  print('Scraper finished!')