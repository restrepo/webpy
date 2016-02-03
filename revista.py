#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
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


def OUTPUT(art,output='udea',verbose=True):
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
        #special output for udea spreasheet format
        date_parts=['year','month','day','volume','article-number']
        for dp in date_parts:
            if dp in art.keys():
                art[dp]=','.join(list(str(art[dp])))
                
        if 'page' in art.keys():
            pages=art['page'].split('-')
            if len(pages)==2:
                art['pages']=','.join(list(str( -eval(art['page']) ) ))
        
        if not 'article-number' in art.keys():
            art['article-number']=','.join(list(str(pages[0])))
                    
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

    rhtml=''; rxml=''
    if output=='udea' and verbose:
        rhtml=rhtml+'''Copy the next table and paste into the Copy sheet of:
               <a href="https://goo.gl/WnSY7M">"Formato revista"</a>,<br/>
               and fill the empy fields in that Copy sheet.<br/>
               Fill (or fix) for ISSN Colciencias, journal country, city and language at: 
               <a href="https://goo.gl/5nfX7c">https://goo.gl/5nfX7c</a><br/>'''
    if output=='udea':
        rhtml=rhtml+'<table border="1">'

    if output=='udea':
        rxml=rxml+'<?xml version="1.0" encoding="UTF-8"?>\n'
        rxml=rxml+'<?xml-stylesheet type="text/xsl" media="screen" href="/~d/styles/atom10full.xsl"?><?xml-stylesheet type="text/css" media="screen" href="http://feeds.feedburner.com/~d/styles/itemcontent.css"?>\n'
        rxml=rxml+'<feed xmlns="http://www.w3.org/2005/Atom" xmlns:openSearch="http://a9.com/-/spec/opensearchrss/1.0/" xmlns:blogger="http://schemas.google.com/blogger/2008" xmlns:georss="http://www.georss.org/georss" xmlns:gd="http://schemas.google.com/g/2005" xmlns:thr="http://purl.org/syndication/thread/1.0" xmlns:feedburner="http://rssnamespace.org/feedburner/ext/1.0">\n'
    
    for k in names.keys():
        if not k in art.keys():
            art[k]=''
            
        if output=='udea':
            rhtml=rhtml+'<tr><td><strong>%s</strong></td><td> %s </td></tr>\n' %(names[k],art[k])

        if output=='udea':
            rxml=rxml+'<entry>\n'
            rxml=rxml+'<title type="text">%s</title><published>%s</published>' %(names[k],art[k])
            rxml=rxml+'</entry>\n'

    if output=='udea':
        rhtml=rhtml+'</table>'
    if output=='udea':
        rxml=rxml+'</feed>\n'

    
    return {'udea_html':rhtml,'udea_xml':rxml,'article':art}
            
if __name__ == "__main__":
    
    cvsout=pd.DataFrame()
    Colciencias=True; verbose=False
    output='udea'
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
        
        xname='revista.xml'
        if art.shape[0]>0:
            ro=OUTPUT(art,output=output)
            print ro['udea_html'].encode('utf-8')
            f=open(xname,'w')
            f.write(ro['udea_xml'].encode('utf-8'))
            f.close()


        if verbose:
            url='http://inspirehep.net/search?p=%s&of=hd' %doi
            response = urllib2.urlopen(url)
            abstract = response.read().split('Abstract')
            if len(abstract)>1:
                print '<strong>Abstract:</strong>%s' %abstract[1]
                
        baseurl='http://gfif.udea.edu.co/python/'
        print '<br/>xml output at %s%s <br/>' %(baseurl,xname)
        jname='revista.json'
        print '<br/>Jason output at %s%s <br/>' %(baseurl,jname)
        
        with open(jname, 'w') as fp:
            json.dump(ro['article'].to_dict(), fp)
        #json load:
        #with open('data.json', 'r') as fp:
        #data = json.load(fp)
