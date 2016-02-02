#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib2
import requests
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth',500)

def read_google_cvs(gss_url="http://spreadsheets.google.com",\
    gss_format="csv",\
    gss_key="0AuLa_xuSIEvxdERYSGVQWDBTX1NCN19QMXVpb0lhWXc",\
    gss_sheet=0,\
    gss_query="select B,D,E,F,I where (H contains 'GFIF') order by D desc",\
    gss_keep_default_na=False
    ):
    """
    read a google spreadsheet in cvs format and return a pandas DataFrame object.
       ....
       gss_keep_default_na: (False) Blank values are filled with NaN
    """
    issn_url="%s/tq?tqx=out:%s&tq=%s&key=%s&gid=%s" %(gss_url,\
                                           gss_format,\
                                           gss_query,\
                                           gss_key,\
                                           str(gss_sheet))
    import urllib2
    import pandas as pd
    gfile=urllib2.urlopen(issn_url)
    return pd.read_csv(gfile,keep_default_na=gss_keep_default_na)


def OUTPUT(art,output='udea'):
    from collections import OrderedDict
    a=''
    if art.to_dict().has_key('author'):
        for d in art.author:
            a=a+'<strong>Autores:</strong> %s %s <br/>\n' %(d['given'],d['family'])
    
            art['autores']=a
        
    art['indexacion']='ISI, Scopus'
    if art.to_dict().has_key('link'):
        art['redirect']='<a href="%s">%s</a>' %(art.link[0]['URL'],\
                                            art.link[0]['URL'])
    if output=='udea':
        names=OrderedDict()
        names['title']=u'Título del articulo'
        names['container-title']='Nombre de la revista'
        names['autores']='Autores'
        names['indexacion']='Indexacion'
        names['DOI']='DOI'
        names['ISSN_colciencias']='ISSN Colciencias'
        names['ISSN_type']='Clasificacion Colciencias'
        names['ISSN']='ISSN'
        names['redirect']='URL'

    r=''
    for k in names.keys():
        if art.to_dict().has_key(k):
            r=r+'<strong>%s:</strong> %s <br/>\n' %(names[k],art[k])

    return r
            
if __name__ == "__main__":
    Colciencias=False
    if sys.argv[1]:
        doi=sys.argv[1]
        
        r=requests.get('http://dx.doi.org/%s' %doi.split('http://dx.doi.org/')[-1],\
                       headers ={'Accept': 'application/citeproc+json'})
        
        r.json()
        if r.json():
            art=pd.Series(r.json())
        
        if Colciencias:
            publindex=read_google_cvs(gss_key='1sAN9w7QYxmONArmhfWMOFoebmGKf1qnkKdHy4OAsjD0',gss_query='select+*')
            art['ISSN_colciencias']=publindex[publindex.TITULO==art['container-title']].ISSN.values[0]
            art['ISSN_type']=publindex[publindex.TITULO==art['container-title']]['CATEGORIA'].values[0]
        else:
            art['ISSN_colciencias']=''
            art['ISSN_type']=''

        if art.shape[0]>0:
            ro=OUTPUT(art)#.enconde('utf-8')
            print ro.encode('utf-8')


        url='http://inspirehep.net/search?p=%s&of=hd' %doi
        response = urllib2.urlopen(url)
        abstract = response.read().split('Abstract')
        if len(abstract)>1:
            print '<strong>Abstract:</strong>%s' %abstract[1]
