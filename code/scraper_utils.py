import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import pandas as pd
import re
import pickle
#from func_timeout import func_timeout, FunctionTimedOut
import os
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib3.exceptions import InsecureRequestWarning



def beautify_url(url):
  # Deze functie plakt http:// voor de url als deze er niet staat
  new_url = url
  if url[:4] != 'http':
    new_url = 'http://' + url
  if url[-1:] == '/':
    new_url = new_url[:-1]
  return new_url


def domain_styles(b_url):
  # Deze functie geeft een lijst van mogelijke domein stijlen terug aan de hand van een url
  # Deze functie is relevant om te vinden welke links er allemaal naar de interne site gaan (zie functie check_inex())

  # Knip http of https
  if b_url[:5] == 'http:':
    url = b_url[7:]
  elif b_url[:5] == 'https':
    url = b_url[8:]
  else:
    url = b_url
  # Knip www.
  if url[:4] == 'www.':
    domain = url[4:]
  else:
    domain = url
  # Check trailin slash (/)
  if domain[-1] != '/':
    domain_noslash = domain
    domain = domain + '/'
  else:
    domain_noslash = domain[:-1]

  styles = [domain, domain_noslash, 'www.'+domain, 'www.'+domain_noslash]
  b_styles = ['http://www.'+domain, 'http://www.'+domain_noslash, 'https://www.'+domain, 'https://www.'+domain_noslash,'http://'+domain, 'http://'+domain_noslash,'https://'+domain, 'https://'+domain_noslash]
  return styles, b_styles


# DEPRECATED
def check_inex(url, href):
  # Deze functie checkt of de link in de href intern is of naar een externe site gaat
  styles, b_styles = domain_styles(url)
  externals = ['http', 'www']
  # check of http erin, zoja check of styles in href zit
  if any(s in href for s in styles):
    return 'internal'
  elif any(s in href for s in externals):
    return 'external'
  else:
    return 'unknown'


def check_href(href):
  # Deze functie checkt of een href werkbaar is voordat de href aan een url parser wordt gegeven

  # Check verboden woorden en tekens en file formats
  skip = ['.index', 'facebook', 'instagram', 'linkedin', 'twitter', '.jpg', '.png']
  if not any(s in href for s in skip) and href!='/' and href!='#' and href!='':
    return_val = True
    # Check :, corrigeer voor http
    if 'http' in href:
      if len(re.findall(':', href))>1:
        return_val = False
      else:
        return_val = True
    else:
      if len(re.findall(':', href))>0:
        return_val = False
      else:
        return_val = True
  else:
    return_val = False
  return return_val


def get_url(url):
  # Deze functie geeft de url terug die de http get request ontvangt. Dit kan na een redirect zijn en is de daadwerkelijke domeinnaam die gebruikt moet worden.beautify_url
  b_url = beautify_url(url)
  headers=set_headers()
  return requests.get(b_url, allow_redirects=True, headers=headers).url


# DEPRECATED
def parse_href(url, href):
  # Deze functie leest een href (die werkbaar is, check met check_href()) en maakt er een leesbare url van mbv meegeleverde url
  link = check_inex(url, href)
  if link == 'external': return None
  elif link == 'internal': return beautify_url(href)
  elif link == 'unknown' and href[0] == '/': return beautify_url(url) + href[1:]
  else: return beautify_url(url) + href


def is_internal(url, href):
  # Deze functie checkt of een href naar een interne of externe pagina gaat
  b_url = beautify_url(url)
  next_url = urljoin(b_url, href)
  base_loc = urlparse(b_url).netloc
  next_loc = urlparse(next_url).netloc
  if next_loc == base_loc: return True
  else: return False


def set_headers():
  # Deze functie geeft de headers voor een user-agent
  return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41'}


def check_url(url):
  # Deze functie checkt de response type van een http get request, wenselijk is een 200 response code
  b_url = beautify_url(url)
  headers=set_headers()
  requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # Verify=False geeft een insecure request warning
  try:
    response = requests.get(b_url, headers=headers, allow_redirects=True).status_code
  except Exception as e:
    raise e
  else:
    response = requests.get(b_url, headers=headers, allow_redirects=True, verify=False).status_code
  return response


def fix_url(url):
  # Deze functie probeert url te repareren door veel voorkomende fouten te verwijderen
  new_url = url.lower()
  new_url = new_url.replace(' ', '')
  new_url = new_url.replace(',', '.')
  if 'www' in new_url and not 'www.' in new_url: new_url.replace('www', 'www.')
  return new_url


def fetch_html(url):
  # Deze functie fetched de html gegeven een url en probeert zoveel mogelijk uitzonderingen te pareren

  # If response 504: try again met verify=False
  # Catch redirect zonder dat het als external wordt gezien
  b_url = beautify_url(url)
  headers = set_headers()
  allow_redirects = True
  response = check_url(b_url)
  requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # Verify=False geeft een insecure request warning
  if response < 200 and response > 299:
    verify = False
    return requests.get(b_url, headers=headers, verify=verify, allow_redirects=allow_redirects).text
  else:
    return requests.get(b_url, headers=headers, allow_redirects=allow_redirects).text


def get_links(url):
  # Deze functie geeft een lijst van hrefs gegeven een url
  links = set()
  b_url = beautify_url(url)
  try:
    html = fetch_html(url)
    soup = BeautifulSoup(html, features='lxml').findAll('a')       
  except:
    return set()
  for link in soup:
    if 'href' in link.attrs:
      href = link.attrs['href']
      links.add(urljoin(b_url, href))
  return links


def index_url(url, max_depth = 2):
  # Deze functie indexeert de hele website gegeven een URL (map van de hele website en interne links), tot een maximale diepte
  depth = 0
  checked = set()
  b_url = beautify_url(url)
  urls = set([b_url])

  while depth <= max_depth:
    temp = urls.copy()
    for url in temp:
      if url not in checked:
        checked.add(url)
        # kijk of link intern is of niet (anders niet get_links)
        links = get_links(url)
        for link in links:
          if check_href(link) and is_internal(b_url, link):
            urls.add(link)
          else:
            urls.add(link)
            checked.add(link)
    depth += 1
  urls.update(checked)
  return urls


def download_docs(index, path='C:\\Temp\\', folder='docs', allow_stream=True):
  # Deze functie download de .pdf en .doc bestanden uit de indexlijst van een url
  headers = set_headers()
  verify = False
  requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # Verify=False geeft een insecure request warning
  if type(index) == str: index = set([index])
  if not os.path.isdir(path+folder): os.mkdir(os.path.join(path, folder))    
  for i in index:
    if is_downloadstream(i):
      try:
        name = find_streamname(i)
        download_stream(i, path=path, folder=folder, filename=name)
      except:
        print('Unable to reach file ...')
        continue
    elif '.pdf' in i or '.doc' in i:
      # Check of folder bestaat
      try:
        if i[-1]=='/': html = requests.get(i[:-1], allow_redirects=True, headers=headers, verify=verify)
        else: html = requests.get(i, allow_redirects=True, headers=headers, verify=verify)
      except:
        print('Unable to reach file ...')
        continue
      name = make_docname(i)
      with open(os.path.join(*[path, folder, name]), 'wb') as f:
        f.write(html.content)


def make_docname(link):
  # Deze functie vind de naam van een document gegeven een url
  if '.pdf' in link: link = link.split('.pdf')[0] + '.pdf'
  elif '.docx' in link: link = link.split('.docx')[0] + '.docx'
  elif '.doc' in link: link = link.split('.doc')[0] + '.doc'

  if link[-1]=='/': name = link[link[:-1].rfind('/')+1:-1]
  else: name = link[link[:-1].rfind('/')+1:]
  name.replace('.', '-')
  return name


def is_downloadstream(url):
  # Deze functie checkt of de url een download stream aan zet (dit is anders dan bv. een file die gehost wordt die je kan downloaden)
  requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
  b_url = beautify_url(url)
  headers = set_headers()
  try:
    head = requests.head(b_url, allow_redirects=True, verify=False, headers=headers).headers
    return 'attachment' in head.get('Content-Disposition', '')
  except:
    return False


def find_streamname(url):
  # Deze functie haalt de filename op van een download stream
  requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
  b_url = beautify_url(url)
  headers = set_headers()
  head = requests.head(b_url, allow_redirects=True, verify=False, headers=headers).headers
  content = head.get('Content-Disposition', '')
  if 'filename' in content:
    name = content.split('filename')[1].replace('=', '').replace('"', '')
    return name
  else:
    return make_docname(url)

def download_stream(url, path='C:\\Temp\\', folder='docs', filename='temp'):
  # Deze functie download een streamed download
  requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
  headers = set_headers()
  b_url = beautify_url(url)
  r = requests.get(b_url, allow_redirects=True, verify=False, stream=True, headers=headers)
  with open(os.path.join(*[path, folder, filename]), 'wb') as f:
    for chunk in r.iter_content(chunk_size=128):
      f.write(chunk)