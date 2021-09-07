# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Enkel scrapen van het web zonder administratie bij te werken

# %%
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from time import sleep, strftime
import pandas as pd
import numpy as np
import datetime as dt
import os
from random import randint

#import urllib
from bs4 import BeautifulSoup

log = True
herstarten = True

pad = 'J:\\Data Science\\Data\\web\\'

#import requests
#import re
#https://realpython.com/python-web-scraping-practical-introduction/
#https://www.dataquest.io/blog/web-scraping-tutorial-python/

#status 0: geen fouten gevonden
#status 1: niet in de doelgroep (BAS, SBAS)
#status 2: niet geldig op de peidatum
#status 3: ongeldige url (syntax)
#status 4: ongeldige url (site niet gevonden)


#todo:
#   doc-documenten als zodanig opslaan
#   pdf's met 0kB bekijken'
#   05HC geeft nog: KeyError: 'content-type'
#   lijsten als input:
#      onderwerpen
#      zoektermen (inclusief de volgorde)
#      aantal pagina's scannen per brin
#      selectiecriteria organisaties
#   maximale tijd te besteden aan een url


# %%
def url_beautify(url):
    url = url.strip()
    if url[:7] != 'http://' and url[:8] != 'https://':
        url = 'http://' + url
    return url
    
def url_controle_syntax(df):
    ok = []
    if log:
        url_fouten = open('c:\\temp\\urls_met_foute_syntax.csv', 'w')
        url_fouten.write('CODE_FUNCTIE;CODE_SOORT;NR_ADMINISTRATIE;fout;url\n')
    for index, regel in df.iterrows():
        url2 = url_beautify(regel['URL'])
        url3 = url2[url2.find("//")+2:]
        fout = ''
        for teken in ',ë:~\\@':
            if fout == '' and teken in url3:
                fout = 'url bevat een "' + teken + '"'
        if fout != '' and log and regel['status'] == 0 :
            #print(url3, ' ', regel['status'], fout)
            url_fouten.write(regel['CODE_FUNCTIE'] + ';' + regel['CODE_SOORT'] +                 ';' + regel['NR_ADMINISTRATIE'] + ';' + fout + ';' + url3 + '\n')
        ok += [fout != '']
    if log:
        url_fouten.close()
    return ok

# geeft de zichtbare tekst van een anchor terug: <a hre...>tekst</a>
def anchor_tekst(tekst):
    t, s = '', 0
    for x in str(tekst):
        if x == '<':
            s += 1
        elif x == '>':
            s -= 1
        elif s == 0:
            t += x
    return t.lower().strip()

# geeft de volledige url van een anchor terug
def anchor_url(tekst, url):
        # tekst is de anchor
        # url is de url van de pagina waarop de link is gevonden
    b, href = False, ''
    for x in tekst.replace(' ','"').split('"'):
        if b == True:                                  #vorige woord was 'href'
            href = x
            b = False
        elif x == 'href=':
            b = True
    if href == '':                                        # geen href in anchor
        return ''
    elif href[:4] == 'http':     #absolute link, kan direct teruggegeven worden
        return href
    url_root = url[:10 + (url + '/')[10:].find('/')]                 #bepaal root
    if href == '/':                                   #verwijzing naar zichzelf
        return url_root
    elif href[0] == '/':          #tekst begint met een slash (sub van de root)
        if url[-1] == '/':
           return url_root + href
        else:
           return url_root + href
    else:                                           #relatieve link in map zelf
        if url[-1:] == '/':
            url_root = url[:-1]
        else:
            url_root = url
        #return url_root[:url_root.rfind('/')] + '/' + href
        return url_root + '/' + href
#print(anchor_url('<a href="bla1.nl">bla2</a>', 'http://bol.com/bla3/bla4/'))
#print(anchor_url('<a href="/">bla2</a>', 'http://www.duo.nl'))

#def link volgen(NR_ADMINISTRATIE, diepte)


# %%
def nu():
    return strftime("%H:%M:%S")
#    return str(dt.datetime.now().hour) + ":" + str(dt.datetime.now().minute) \
#        + ":" + str(dt.datetime.now().second)
# print(nu())


# %%
def simple_get(url):
    try:
        with closing(get(url)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        return None
def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


# %%
# laad of herlaad de lijst met urls.
if herstarten:
    print('maak urllijst')
    df = pd.read_csv(r'J:\Data Science\Data\Brin\org_url\org_url_20191212.txt', sep='\t' )
    df['DT_EINDE_RECORD'].fillna(21001231, inplace = True)
#    df['DT_EINDE_RECORD'] = df['DT_EINDE_RECORD'].astype('int64', inplace = True)
    df['status'] = 0
    df['status_dat'] = dt.datetime.now()
    df.to_csv(pad + 'urllijst.csv', sep='\t', encoding='utf-8', index=False)
else:
    print('laad urllijst')
    df = pd.read_csv(pad + 'urllijst.csv', sep='\t', encoding='utf-8')
    
print(df.loc[df['status'] == 0].shape)
# , encoding='utf-8'


# %%



# %%
# bekijk enkel de url's met een geldige syntax:
controle = url_controle_syntax(df)
df.loc[controle, ['status', 'status_dat']] = [3, dt.datetime.now()]
print(df.loc[df['status'] == 0].shape)
df.to_csv(pad + 'urllijst.csv', sep='\t', encoding='utf-8', index=False)


# %%
# bekijk enkel url's geldig op de prikdatum:
prikdatum = 20181001
df.loc[(df.DT_BEGIN_RECORD > prikdatum) | (prikdatum > df.DT_EINDE_RECORD), ['status', 'status_dat']] = [2, dt.datetime.now()]
print(df.loc[df['status'] == 0].shape)


# %%
# selectie bij het scannen:

# bekijk enkel de basisscholen:
if False:
    df.loc[df['CODE_SOORT'] != 'BAS', ['status', 'status_dat']] = [1, dt.datetime.now()]

# of enkel alle brin4's
#df.loc[df['CODE_FUNCTIE'] != 'U', ['status', 'status_dat']] = [1, dt.datetime.now()]

print(df.loc[df['status'] == 0].shape)


# %%
df["status"].value_counts()


# %%
########################################
print('laad urllijst')
df = pd.read_csv(pad + 'urllijst.csv', sep='\t', encoding='utf-8')
df.loc[df['status'] == 0].sort_values(by='NR_ADMINISTRATIE').head()


# %%
def anchor_verwerken(instelling, anchor, url_vorig, diepte, themas):
        # input: instelling: BRIN
        # input: anchor: de volledig gevonden hyperlink
        # input: url_vorig: pagina vanuitwaar dehyperlink wordt aangeroepen (ivm relatieve links)
        # input: diepte: nivo van recusie
        # input: docsoorten: bijvoorbeeld ['schoolgids', 'jaarverslag']
        # rv: document dat gevonden is met soort en jaar
        # rv: lijst met url's om ook de te werken
    return [succes, ['schoolgids_2017', 'jaarverslag 2016']]

def document_opslaan(NR_ADMINISTRATIE, soort, url):
    jaren = bepaal_jaren(url)
    for jaar in jaren:
        print('Sla', soort, '-document op in', pad, '/', str(jaar), '/', NR_ADMINISTRATIE)


# %%
def zoeklijst_uitbreiden(lijst, tekst, url):
#    print(92, tekst)
#    if 'oo' not in tekst:                        #tijdelijke beperking van urls
#        return
    if tekst == '':                          #bedenk een label als dit nodig is
    #if tekst in ('', '/'):                  #bedenk een label als dit nodig is
        t = url[url.replace('//','__').find('/'):]
    else:
        t = tekst.lower()
#    print(93, t)
    u = url.split("#")[0]
    if t in lijst.keys():                             #schermtekst komt al voor
        if not u in lijst[t]:                                #maar url nog niet
            lijst[t] += [u]
    else:                                       #schermtekst komt nog niet voor
        lijst[t] = [u]


# %%
#zoeklijst = {'start': ['http://www.hetsterrenlicht.nl/School/Schoolgids']}
#        while len(zoeklijst) > 0 and todo != [] and zoek_n > 0: #scan zoeklijst
#            print('zoeklijst:', zoeklijst)
#            print('gedaan:', gedaan)
#                print("deze url al gedaan")
#                print(96, zoek_n)
#                print(99, zoek_n, len(str(pagina)))
#                    print(95, anchor)
#                        print(98)
#                    print(72, anchor.contents)
#                    print(94, len(zoeklijst), url_totaal)
#            print('------', zoek_n, len(zoeklijst), len(gedaan))


# %%
def bedenk_naam(url, org, onderwerp, tekst):
    if   '2010' in url or '1011' in url or '10-11' in url or '2010' in tekst:
        j = '2010'
    elif '2011' in url or '1112' in url or '11-12' in url or '2011' in tekst:
        j = '2011'
    elif '2012' in url or '1213' in url or '12-13' in url or '2012' in tekst:
        j = '2012'
    elif '2013' in url or '1314' in url or '13-14' in url or '2013' in tekst:
        j = '2013'
    elif '2014' in url or '1415' in url or '14-15' in url or '2014' in tekst:
        j = '2014'
    elif '2015' in url or '1516' in url or '15-16' in url or '2015' in tekst:
        j = '2015'
    elif '2016' in url or '1617' in url or '16-17' in url or '2016' in tekst:
        j = '2016'
    elif '2017' in url or '1718' in url or '17-18' in url or '2017' in tekst:
        j = '2017'
    elif '2018' in url or '1819' in url or '18-19' in url or '2018' in tekst:
        j = '2018'
    elif '2019' in url or '1920' in url or '19-20' in url or '2019' in tekst:
        j = '2019'
    else:
        j = '0000'
        print('pas de functie bedenk_naam aan omdat geen jaar bepaald kon worden')
    naam = onderwerp + '_' + j  + '_' + org
    url2 = url.split("?")[0].lower()           #verwijder tekst naar vraagteken
    if url2.endswith(('.pdf')):
        return naam + '.pdf'
    elif url2.endswith(('.doc')):
        return naam + '.doc'
    elif url2.endswith(('.docx')):
        return naam + '.docx'
    else:
        print(132, 'onbekend type')
        print(133, url)
        print(133, url2)
        print(134, tekst)
        q = 1 / 0
        return naam + '.onbekend'
#print(bedenk_naam("http:\\bla_2015-2019", '00AH', 'jaarverslag', 'bla'))


# %%
def document_downloaden(u_link, NR_ADMINISTRATIE, soort, u_tekst):
    naam = bedenk_naam(u_link, NR_ADMINISTRATIE, todo_i, u_tekst)
    print('downloaden:', naam, 'u_link')
    with open('c://temp//' + naam, 'wb') as f:
        f.write(get(u_link).content)


# %%
# kies uit de zoeklijst de meest waarschijnlijke url
def url_kiezen(d):
    #lijst met termen in aflopen prioriteit:
    zoektermen = ['schoolgids', 'schooldocumenten', 'download',                       'download schoolgids', 'downloads', 'organisatie', 'documenten',              'schoolplan', 'onze school', 'documentatie', 'school', 'jaargids',            'jaarverslag', 'informatie', 'informatiekaart', 'voor ouders',                'jaarplanning', 'informatiegids', 'organisatie', 'ouderplein',                'publicaties', 'praktisch']
    # bij 1 element stuur kies de eerste
    if len(d) == 1:
        return (list(d.keys())[0], d[list(d.keys())[0]][0])
    
    for w in zoektermen:                              #doorloop alle zoektermen
        
        # zoek naar PDF's in urls
        for k in d.keys():                                        #loop teksten
            for u in d[k]:                            #loop urls van elke tekst
                if u.endswith(tuple([".pdf", ".pdf?"])):
                    if u.find(w) > -1:            #als zoekterm voorkomt in url
                        return (k, u)
        
        # zoekterm gelijk aan complete tekst
        for k in d.keys():                                        #loop teksten
            if k.find(w) > -1:                  #als zoekterm voorkomt in tekst
                return [k, d[k][0]]
        
        # zoekterm gelijk aan deel tekst
        for k in d.keys():                                        #loop teksten
            if u.find(w) > -1:                    #als zoekterm voorkomt in url
                return (k, u)

        # deel zoekterm gelijk aan tekst
        for k in d.keys():                                        #loop teksten
            if w.find(k) > -1:                    #als zoekterm voorkomt in url
                return (k, u)

    # kies de eerste (oudste) link van de eerste term
    return (list(d.keys())[0], d[list(d.keys())[0]][0])


# %%
# een paar scholen negeren omdat deze nog fouten opleveren
if True:
    df.loc[df['NR_ADMINISTRATIE'].isin(['00BW', '00CU', '00EI', '00ML',
        '00KM40', '00ML00', '00MP', '00MV', '00RK', '02GD', '02GD00', '02PQ00',
        '02RM', '02WU00', '03HH', '03IC', '03LR', '03WL00', '03XB00', '04GX01', '04IK00', '04JR', '04KC', 
        '04MZ', '04VG', '04VG00', '04VH', '05IL00', '05JZ00', '05OP00', '05RV', '05TN',
        '05TN00', '05TS', '05YL', '05YL00', '05ZW', '06EI', '06LH', '06NI', '06NI00', '06PI', '07EC',
        '08JE00', '08KC', '08NF', '08NP', '08TL00', '09LK', '09LK00', '09OA00', '09VY00', '10JM',
        '10JT', '10NH', '10NL', '10PO', '10QE', '10QY', '10UF', '10UF00', '11AY00', 
        '11UH00', '12BF00', '12CL00', '12GN00', '12VA', '12VA00', '12ZL ', '13603', '13OW00', '13VC00', '15SZ', '15TL', 
        '13OW01', '13WM', '13WM00', '14RC', '15SZ', '15TL', '15VQ', '15VQ00', 
        '16JK', '16JK00', '16WH00', '17NQ', '17NQ00', '17OB', '17OB01', 
        '17OF', '17OF00', '17PB', '17PB00', '17QF', '17QF00', '17XW00', '18CH10', 
        '18PQ', '18PQ00', '18SP',
        '18SP00', '18SU', '18ZG00', '19CA00', '19MZ', '19MZ00', '19QL', '20127', 
        '20AA', '20DG', '20JQ00', '21GW', '21GW00', '21GW01', '21GW02', '21HC12',
        '23DJ', '23DR', '23RC', '23RC00', '23ZW00', '25KE', '25KE00', '26AC', '26AW', 
        '26AW00', '28CD', '28LC00', '29XL', '30837', '30BE', '30PW', '30UF', '30UN',
        '30UR00', '31028', '31162', '31FM', '31FM00',
        '40075', '35647', '40180', '40646', '40648', '40945', '41282', '41407', '41490', '41509',
        '41812', '42616', '48622', '76753', '84215', '87205', '94771', '99048', '99060', '99711', 
        'VO2507', 'VO2810', 'VO2307']), 'status'] = 8
df["status"].value_counts()


# %%
# scan de sites ####################################################
for index, regel in df.sample(frac=1).iterrows():
#for index, regel in df[632:].iterrows():                           #max: 49842, 2937
    if regel['status'] == 0:
        print(nu(), 'instelling: ', regel['NR_ADMINISTRATIE'], index)
        zoeklijst = {'start': [url_beautify(regel['URL'])]}    #nog te bekijken
        gedaan = []
        todo = ['informatiegids', 'jaarkalender', 'jaarplan', 'jaarrekening', 
            'jaarverslag', 'schoolinformatieboekje', 'schoolgids',
            'schoolplan', 'schoolondersteuningsprofiel']
        zoek_n = randint(2,40)
        #zoek_n = 25                    # zo vaak per brin zoeken naar goede url
        while len(zoeklijst) > 0 and zoek_n > 0:                #scan zoeklijst
            u_tekst, u_link = url_kiezen(zoeklijst)
            if u_link in gedaan:                                #link al gedaan
                if len(zoeklijst[u_tekst]) == 1:      #enige link van een tekst
                    del zoeklijst[u_tekst]  #verwijder u_tekst uit de zoeklijst
                else:
                    zoeklijst[u_tekst] = zoeklijst[u_tekst][1:]   #verw 1e link
                continue
            print(' -', zoek_n, len(zoeklijst), len(gedaan), 'Gekozen url:', u_link, '"' + u_tekst + '"')
            if u_link.split("?")[0].lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                for todo_i in todo:
                    if todo_i in u_link.lower() or todo_i in u_tekst:
                        document_downloaden(u_link, regel['NR_ADMINISTRATIE'], todo_i, u_tekst)
            else:                                                 #volg de link
                try:
                    pagina = simple_get(u_link)
                except KeyError:
                    pass
                soup = BeautifulSoup(str(pagina),'html.parser')
                for anchor in soup.find_all('a'):
                    if str(anchor).find('href') < 0:
                        continue
                    if anchor.contents == []:
                        tekst = ''
                    else:
                        tekst = str(anchor.contents[0])
                    url_totaal = anchor_url(str(anchor), u_link)
                    zoeklijst_uitbreiden(zoeklijst, tekst, url_totaal)
            gedaan += [u_link]
            zoek_n -= 1
            sleep(1.1)
        #print('einde organisatie:', regel['NR_ADMINISTRATIE'], len(zoeklijst))                                  


# %%



