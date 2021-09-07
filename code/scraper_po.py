from scraper_utils import *
from func_timeout import func_timeout, FunctionTimedOut

def run_scraper():
  # Deze functie runt de scraper
  
  # Laad data
  orgs = 'I:\Team Data-Science\Projecten\webscraper\data\org_url_20210511.txt'
  orgs_df = pd.read_csv(orgs, delimiter = "\t")
  urls_nr = orgs_df[['NR_ADMINISTRATIE', 'URL']][orgs_df['CODE_SOORT']=='BAS'].drop_duplicates(subset='URL').values

  # Maak variables
  exceptions = set()
  failed_downloads = set()
  indices = dict()
  doc_path = 'C:\\Users\\ad010sup\\Documents\\schooldocumenten\\docs\\'
  exc_path = 'C:\\Users\\ad010sup\\Documents\\schooldocumenten\\exceptions\\'
  fd_path = 'C:\\Users\\ad010sup\\Documents\\schooldocumenten\\failed_downloads\\'
  count = 0

  for nr, url in urls_nr:
    count += 1
    print(f'Checking:  {nr}  {url}, {count} of {len(urls_nr)}')
    if os.path.isdir(doc_path+nr) and not os.listdir(doc_path+nr) and '31' in nr:
      try:
        print('Indexing ...')
        #index = func_timeout(180, index_url, args=(url, 2))
        url = fix_url(url)
        b_url = beautify_url(url)
        b_url = get_url(b_url)
        index = index_url(b_url, 2)
      except FunctionTimedOut:
        print('Indexing timed out ...')
        exceptions.add(b_url)
        continue
      except:
        print('Failed to index ...')
        exceptions.add(b_url)
        continue

      try:
        print('Saving document locations!')
        download_docs(index, path=doc_path, folder=nr)
      except:
        print('Failed to download!')
        failed_downloads.add(b_url)
    else:
      print('Folder/files already exist, next ->')

  with open(fd_path+'failed_downloads.pkl', 'wb') as f:
    pickle.dump(failed_downloads, f, protocol=pickle.HIGHEST_PROTOCOL)

  with open(exc_path+'scraper_exceptions.pkl', 'wb') as f:
    pickle.dump(exceptions, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
  run_scraper()
  print('Scraper finished!')