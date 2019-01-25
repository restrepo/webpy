#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import unidecode
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
    
import requests
import pandas as pd
from datetime import datetime
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth',500)

def add_blank_missing_keys(art,keys):
    '''
    Check if the keys are in a Pandas Series.
    If not the key value is initialized with
    the empty string
    '''
    for k in keys:
        art[k]=art.get(k)
    #Replace None with empty string
    return art.fillna('')    

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
    import pandas as pd
    gfile=urlopen(issn_url)
    return pd.read_csv(gfile,keep_default_na=gss_keep_default_na)

def date_parts(art):
    #http://stackoverflow.com/questions/8142364/how-to-compare-two-dates
    if 'created' in art.keys():
        if art['created']: #assume that 'date-parts' is defined
            kd='created'
        if 'issued' in art.keys():
            if art['issued']:
                kd='issued' # overwrite previous kade
            if art['created'] and art['issued']: #requires both!
                if   len(art['created']['date-parts'][0])>=3 and len(art['issued']['date-parts'][0])< 3:
                    kd='created'
                elif len(art['created']['date-parts'][0])< 3 and len(art['issued']['date-parts'][0])>=3:
                    kd='issued'
                elif len(art['created']['date-parts'][0])>=3 and len(art['issued']['date-parts'][0])>=3:
                    if datetimelist( art['created']['date-parts'][0] ) <=\
                       datetimelist( art['issued']['date-parts'][0] ):
                        kd='created'
                    else:
                        kd='issued'
                else:
                    kd='created'

    else:
        kd='unknown'
        art[kd]={'date-parts':[[6666,12,31]]}
                
    if len(art[kd]['date-parts'][0])>=1:
        art['year']=art[kd]['date-parts'][0][0]
    if len(art[kd]['date-parts'][0])>=2:
        art['month']=art[kd]['date-parts'][0][1]
    if len(art[kd]['date-parts'][0])>=3:
        art['day']=art[kd]['date-parts'][0][2]

    return art


def OUTPUT(art,output='udea',verbose=True):
    import time
    import re
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
    
    
    art=date_parts(art)

                
    if output=='udea':
        #special output for udea spreasheet format
        date_parts=['year','month','day','volume','article-number']
        for dp in date_parts:
            if dp in art.keys():
                art[dp]=','.join(list(str(art[dp])))
                
        #Prefered format for page is 'article-number'. Choose page or issue if not 'article-number'
        if 'page' in art.keys():
            pages=art['page'].split('-')
            if len(pages)==2:
                clean_pages=re.sub( r'\-0+([0-9])',r'-\1',re.sub( r'^0+([0-9])',r'\1',art['page'] ) )
                art['pages']=','.join(list(str( -eval(clean_pages)+1 ) ))
        elif 'issue' in art.keys():
            pages=[art['issue']]
        else:
            pages=['']
            
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
        rhtml=rhtml+'''<h3>Datos generales de la producci&oacute;n</h3>
                      T&iacute;tulo de la publiaci&oacute;n<br/>
                      <input type="text" value="{}" size="100"><br/>'''.format(art['title'])
    if output=='udea':
        rhtml=rhtml+'<table border="0" index="0">'

    if output=='udea':
        rxml=rxml+'<?xml version="1.0" encoding="UTF-8"?>\n'
        rxml=rxml+'<?xml-stylesheet type="text/xsl" media="screen" href="/~d/styles/atom10full.xsl"?><?xml-stylesheet type="text/css" media="screen" href="http://feeds.feedburner.com/~d/styles/itemcontent.css"?>\n'
        rxml=rxml+'<feed xmlns="http://www.w3.org/2005/Atom" xmlns:openSearch="http://a9.com/-/spec/opensearchrss/1.0/" xmlns:blogger="http://schemas.google.com/blogger/2008" xmlns:georss="http://www.georss.org/georss" xmlns:gd="http://schemas.google.com/g/2005" xmlns:thr="http://purl.org/syndication/thread/1.0" xmlns:feedburner="http://rssnamespace.org/feedburner/ext/1.0">\n'
        rhtml=rhtml+'<tr><td>N&uacute;mero total de autores</td><td> Idioma original </td></tr>\n'
        rhtml=rhtml+'<tr><td><input type="text" value="{}"> </td><td> <input type="text" value="{}">  </td></tr>\n'.format(
            len( art['autores'].split('<br/>') )-1 ,art['language'])  
    
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

def get_colciencias(art,publindex):
    if 'CATEGORIA' in publindex:
        colciencias=publindex[(publindex.TITULO.str.lower()).str.contains(\
            art['container-title'].lower())].sort_values('CATEGORIA')[:1]    
        if len(colciencias)==0: #Journal name not found. Try by ISSN
            if 'ISSN' in art.keys():
                if type(art['ISSN'])==list and len(art['ISSN'])>0:
                    colciencias=pd.DataFrame()
                    for issn in art['ISSN']:
                        colciencias=colciencias.append( publindex[publindex['ISSN']==issn] )
                    

                        
        return colciencias.sort_values('CATEGORIA')[:1]
    else:
        return pd.DataFrame()

def add_colciencias_issn(art,Colciencias=True):
    
    if Colciencias:    
        if 'container-title' in art.keys():
            publindex=read_google_cvs(gss_key='1sAN9w7QYxmONArmhfWMOFoebmGKf1qnkKdHy4OAsjD0',gss_query='select+*')
            publindex=publindex.rename_axis({'Unnamed: 0':'CATEGORIA',
                                         'ISSN':'ISSN_colciencias'},axis='columns')
            df_colciencias=get_colciencias(art,publindex)
            if len(df_colciencias)==0:
                publindex=read_google_cvs(gss_key='1umgapW8KOIPqmu_hyjon3n2SXbnbDlmnRnXzjUHcXHE',gss_query='select+*')
                df_colciencias=get_colciencias(art,publindex)
                #store in database issn.csv and update manually
            
            if len(df_colciencias)>0:
                for k in ['ISSN_colciencias','country','city','lenguage']:
                    if k in df_colciencias:
                        art[k]=df_colciencias[k].values[0]#.decode('utf-8')
                #art['ISSN_colciencias']=df_colciencias['ISSN'].values[0].decode('utf-8')
                #art['ISSN_type']       =df_colciencias['CATEGORIA'].values[0].decode('utf-8')
                #art['country']         =df_colciencias['country'].values[0].decode('utf-8')
                #art['city']            =df_colciencias['city'].values[0].decode('utf-8')
                #art['lenguage']        =df_colciencias['language'].values[0].decode('utf-8')                
                
        else:
            if Colciencias:
                f=open("ERRORS",'a')
                f.write("art[container-title]  empty for DOI: %s" %art['DOI'])
                f.close()

        if 'country' in art:
            if 'publisher' in art and len(art['country'])==0:
                if  art['publisher'].find('Elsevier')!=-1:
                    art['country']='Holanda'
                    art['city']='Amsterdam'
                    art['language']='English'


        return art
    
def datetimelist(l):
    if len(l)==1:
        return datetime(l[0],12,31)
    elif len(l)==2:
        d=30
        if l[1]==2: d=28
        return datetime(l[0],l[1],30)
    else:
        return datetime(l[0],l[1],l[2])

def get_doi(doi,crossref=False):
    import requests
    if not crossref:
        r=requests.get('http://dx.doi.org/%s' %doi.split('http://dx.doi.org/')[-1],\
                       headers ={'Accept': 'application/citeproc+json'})
        rjson=r.json()
    else:
        r=requests.get('http://api.crossref.org/works/%s' %doi.split('http://dx.doi.org/')[-1])
        rjson=r.json()['message']
        
    return  rjson

def html_out(art):
    rhtml='''<!DOCTYPE html>
    <html lang="en"> 
    <head>
    <meta charset="utf-8"/>
    </head>
    <body>
    <h4>Despu&eacute;s de ingresar al portal, copie y pegue <a href="http://asone.udea.edu.co/puntajeDocente/#/consultarSolicitudesDocentes">aqu&iacute;</a></h4>

    <h3>Datos generales de la producci&oacute;n</h3>'''
    try:
        # Python2 enconding problem
        title=( art['title'] ).encode('ascii','replace').replace('\n','')
    except TypeError:
        title=( art['title'] ).replace('\n','')
        
    rhtml=rhtml+'''
      T&iacute;tulo de la publiaci&oacute;n<br/>
      <input type="text" value="{}" size="100"><br/>'''.format(title )


    rhtml=rhtml+'<table border="0" index="0">'
    rhtml=rhtml+'<tr><td>N&uacute;mero total de autores</td><td> Idioma original </td></tr>\n'    
    rhtml=rhtml+'<tr><td><input type="text" value="{}"> </td><td> <input type="text" value="{}">  </td></tr>\n'.format(
               len(art.author) ,art.language)
    
    rhtml=rhtml+'<tr><td>Mes/A&ntilde;o de la publicaci&oacute;n</td><td> Pa&iacute;s de la Publicaci&oacute;n </td></tr>\n'
    rhtml=rhtml+'<tr><td><input type="text" value="{:02d}/{}"> </td><td> <input type="text" value="{}">  </td></tr>\n'.format(
            art.month,str(art.year),art.country)    
    
    rhtml=rhtml+'<tr><td>Departamento/Estado de la publicaci&oacute;n</td><td> Ciudad de Publicaci&oacute;n </td></tr>\n'
    rhtml=rhtml+'<tr><td><input type="text" value=""> </td><td> <input type="text" value="{}">  </td></tr>\n'.format(
                  art.city)
    rhtml=rhtml+'</table>'
    
    #Creditos
    rhtml=rhtml+'<h3>Datos espec&iacute;ficos de la producci&oacute;n</h3>'
    rhtml=rhtml+'<table border="0" index="0">'
    
    if art.ISSN_colciencias:
        ISSN=art.ISSN_colciencias
    else:
        ISSN=art.ISSN[0]    
    rhtml=rhtml+'<tr><td>Nombre de la revista</td><td> ISSN </td></tr>\n'
    rhtml=rhtml+'<tr><td><input type="text" value="{}"> </td><td> <input type="text" value="{}">  </td></tr>\n'.format(
            art['container-title'] ,ISSN)
    
    try: 
        OA=pd.DataFrame( art.license ).get('URL').str.lower().str.contains('creativecommons')
        OA=OA[OA]
    except AttributeError:
        OA=pd.DataFrame()

    if OA.size:
        art['Open_Access']='Si'
    else:
        art['Open_Access']='No'
    
    rhtml=rhtml+'<tr><td>Es de acceso abierto</td><td> Documento adjunto(Si es de acceso abierto) </td></tr>\n'
    rhtml=rhtml+'<tr><td><input type="text" value="{}"> </td><td> <input type="text" value="">  </td></tr>\n'.format(
           art['Open_Access'])

    url='https://doi.org/{}'.format(art.DOI)
    rhtml=rhtml+'<tr><td>Registro DOI</td><td> URL del art&iacute;culo </td></tr>\n'
    rhtml=rhtml+'<tr><td><input type="text" value="{}"> </td><td> <input type="text" value="{}">  </td></tr>\n'.format(
            art.DOI,url)
    
    rhtml=rhtml+'<tr><td>N&uacute;mero</td><td> Volumen de la revista </td></tr>\n'
    rhtml=rhtml+'<tr><td><input type="text" value="{}"> </td><td> <input type="text" value="{}">  </td></tr>\n'.format(
            art.volume ,art['article-number'])

    rhtml=rhtml+'<tr><td>Instituci&oacute;n que publica</td><td>  </td></tr>\n'
    rhtml=rhtml+'<tr><td><input type="text" value="{}"> </td><td>   </td></tr>\n'.format(
            art.publisher )
    
    rhtml=rhtml+'</table>'
    rhtml=rhtml+'''
    <br/>
    <br/>
    Edite manualmente el pa&iacute;s y la ciudad de la revista <a href="https://docs.google.com/spreadsheets/d/1sAN9w7QYxmONArmhfWMOFoebmGKf1qnkKdHy4OAsjD0/edit#gid=1189451937">AQU&Iacute;</a>.  Para futuros usos.
    </body>
    </html>'''
    return rhtml
    
if __name__ == "__main__":
    cvsout=pd.DataFrame()
    Colciencias=True; verbose=False
    output='udea'
    if sys.argv[1] !='-f':
        doi=sys.argv[1]
    
    
    rjson=get_doi(doi)
    if rjson:
        art=pd.Series(rjson,)
    
    #Add info of Publindex base in maximun category of the Journal
    art=add_colciencias_issn(art,Colciencias)    
    
    # Be sure that all the used keys be proper (re)intialized here:
    keys=['title','author','languages','month','year','country','city',
         'container-title','ISSN','ISSN_colciencias','Open_Access',
         'volume','article-number','publisher']
    art=date_parts(art)
    art=add_blank_missing_keys(art,keys)
    rhtml=html_out(art)
    print(rhtml.encode('utf-8'))

