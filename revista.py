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
    import time
    from collections import OrderedDict
    a=''
    if 'author' in art.keys():
        for d in art.author:
            a=a+'%s %s <br/>\n' %(d['given'],d['family'])
    
            art['autores']=a
        
    art['indexacion']='ISI, Scopus'
    if 'link' in art.keys():
        art['redirect']='<a href="%s">%s</a>' %(art.link[0]['URL'],\
                                            art.link[0]['URL'])
    if 'issued' in art.keys(): 
        if 'date-parts' in art['issued'].keys():
            if len(art['issued']['date-parts'][0])>=1:
                art['year']=art['issued']['date-parts'][0][0]
            if len(art['issued']['date-parts'][0])>=2:
                art['month']=art['issued']['date-parts'][0][1]
            if len(art['issued']['date-parts'][0])>=3:
                art['day']=art['issued']['date-parts'][0][2]
                
    if output=='udea':
        date_parts=['year','month','day','volume','article-number']
        for dp in date_parts:
            if dp in art.keys():             
                art[dp]=','.join(list(str(art[dp])))
                    
        tl=time.localtime()
        art['date-year']=','.join(list(str( tl.tm_year  )))
        prtm=''; prtd=''
        if tl.tm_mon<10:
            prtm='0'
        if tl.tm_mday<10:
            prtd='0'
        art['date-month']=','.join(list(prtm+str( tl.tm_mon  )))
        art['date-day']=','.join(list(prtd+str( tl.tm_mday  ))) 
            
    if output=='udea':
        names=OrderedDict()
        names['title']=u'Título del artículo'
        names['container-title']='Nombre de la revista'
        names['DOI']='DOI'
        names['publisher']=u'Institución que publica'
        names['country']=u'País'
        names['city']=u'Ciudad'
        names['ISSN_colciencias']='ISSN Colciencias'
        names['language']='Idioma'
        names['year']=u'Año'
        names['month']='Mes'
        names['day']=u'Día'
        names['volume']='Volumen'
        names['article-number']=u'Número'
        names['pages']=u'Nro páginas'
        names['tiraje']=u'Tiraje'
        names['revista']='Revista'
        names['fotocopia']='Fotocopia'
        names['otro']='Otro'
        names['date-year']=u'Fecha presentación: Año'
        names['date-month']=u'Fecha presentación: Mes'
        names['date-day']=u'Fecha presentación: Día'
        names['autores']='Autores'
        names['ISSN_type']=u'Clasificación Colciencias'
        names['ISSN']='ISSN'
        names['redirect']='URL'

    r=''
    if output=='udea':
        r=r+'''Copy the next table and paste into the Copy sheet of:
               <a href="https://goo.gl/WnSY7M">"Formato revista"</a>,<br/>
               and fill the empy fields in that Copy sheet.<br/>
               Fill (or fix) for ISSN Colciencias, journal country, city and language at: 
               <a href="https://goo.gl/5nfX7c">https://goo.gl/5nfX7c</a><br/>'''
    r=r+'<table border="1">'
    
    for k in names.keys():
        if not k in art.keys():
            art[k]=''
            
        r=r+'<tr><td><strong>%s</strong></td><td> %s </td></tr>\n' %(names[k],art[k])
    r=r+'</table>'
    return r
            
if __name__ == "__main__":
    Colciencias=True
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
            art['country']=publindex[publindex.TITULO==art['container-title']]['country'].values[0].decode('utf-8')
            art['city']=publindex[publindex.TITULO==art['container-title']]['city'].values[0].decode('utf-8')
            art['language']=publindex[publindex.TITULO==art['container-title']]['language'].values[0].decode('utf-8')
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
