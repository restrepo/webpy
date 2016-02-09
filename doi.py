#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Search doi by title and fist author surname
    based on https://github.com/torfbolt/DOI-finder
    See: http://www.crossref.org/guestquery/#textsearch
'''

lower_first_char = lambda s: s[:1].lower() + s[1:] if s else ''
def search_doi(surname='Florez',\
    title=r'Baryonic violation of R-parity from anomalous $U(1)_H$',other=''):
    '''
    Search doi from http://search.crossref.org/ 
    '''
    import re
    import requests
    doi={}
    search=''
    if surname:
        search=surname
    if title:
        if len(search)>0:
            search=search+', '+title
    if other:
        if len(search)>0:
            search=search+', '+other
            
    r=requests.get('http://search.crossref.org/?q=%s' %search)
    urldoi='http://dx.doi.org/'
    doitmp=r.text.split(urldoi)[1].split("\'>")[0].replace('&lt;','<').replace('&gt;','>')
    if doitmp:
        json='https://api.crossref.org/v1/works/'
        rr=requests.get( json+urldoi+doitmp )
        if rr.status_code==200:
            if rr.json().has_key('message'):
                chktitle = re.sub(r"\$.*?\$","",title) # better remove all math expressions
                chktitle = re.sub(r"[^a-zA-Z0-9 ]", " ", chktitle).split(' ')
                if chktitle:
                    if not -1 in [(rr.json()["message"]['title'][0]).find(w)  for w in chktitle]:
                        doi=rr.json()["message"]
                    
    return doi
    
def general_search_doi(surname='Florez',\
    title=r'Baryonic violation of R-parity from anomalous $U(1)_H$'):
    '''
    Search doi from http://search.crossref.org/ with special format
    '''
    doi=search_doi(surname,title)
    if doi.has_key('author'):
        doi['Author']=doi['author'][0]['family']
    if doi.has_key('title'):                
        doi['Article Title']=doi['title'][0]                                            
    if doi.has_key('container-title') and len(doi['container-title'])==2:                    
        doi['Journal Title']=doi['container-title'][1]                        
    if doi.has_key('published-online'):                    
        doi['Year']=str(doi['published-online']['date-parts'][0][0])
    for k in ['Volume','Issue','Page']:                    
        if doi.has_key(lower_first_char(k)):                        
            doi[k]=doi['volume']                                                 
                        
    return doi

def searchdoi(title='a model of  leptons', surname='Weinberg'):
    """
    based on https://github.com/torfbolt/DOI-finder
    See: http://www.crossref.org/guestquery/
    
    Search for the metadata of given a title; e.g.  "A model of  leptons" 
   (case insensitive), and the Surname (only) for the first author, 
    e.g. Weinberg 
                      
    returns a dictionary with the keys:

       ['Article Title','Author','ISSN','Volume','Persistent Link','Year',
        'Issue','Page','Journal Title'],

       where 'Author' is really the surname of the first author
    """
    import mechanize
    import re
    from bs4 import BeautifulSoup
    
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', 'Firefox')] 
    browser.open("http://www.crossref.org/guestquery/")
    assert browser.viewing_html()
    browser.select_form(name="form2")
    # use only surname of first author
    browser["auth2"] =  surname
    browser["atitle2"] = title
    response = browser.submit()
    sourcecode = response.get_data()
    result = re.findall(r"\<table cellspacing=1 cellpadding=1 width=600 border=0\>.*?\<\/table\>" ,sourcecode, re.DOTALL)
    if len(result) > 0:
        html=result[0] 
        if re.search('No DOI found',html):
            html='<table><tr><td>No DOI found<td></tr></table>'
    else:
        doi={}
        #return {}         

    soup = BeautifulSoup(html)
    table = soup.find("table")

    dataset = []
    for row in table.find_all("tr"):
        for tdi in row.find_all("td"):
            dataset.append(tdi.get_text())
            
    if len(dataset)==20:
        headings=dataset[:9]
        datasets=dataset[10:-1]
        doi=dict(zip(headings,datasets))
        
    else:
        doi={}
        
    if doi:
        if doi.has_key('ISSN') and doi.has_key('Persistent Link'):
            doi[u'URL']=doi['Persistent Link']
            doi[u'DOI']=doi['Persistent Link'].split('http://dx.doi.org/')[-1]

            
    return doi

if __name__ == "__main__":
    import sys
    import re
    title='';first_author_surname=''
    if sys.argv[1]:
        title=sys.argv[1]
    if sys.argv[2]:
        first_author_surname=sys.argv[2]
        
    d=searchdoi(title,first_author_surname)
    if not d:
        print 'General search:<br/>'
        d=general_search_doi(first_author_surname,title)
        
    ref='';sep=','
    for k in ['Author','Article Title','Journal Title','Volume','Issue','Page','Year']:
        if d.has_key(k):
            if k=='Author':
                d['Author'] = re.sub(r"[^a-zA-Z0-9 ]", " ",d['Author'] ) #remove non standard characters 
            if k=='Volume':
                d[k]='<strong>%s</strong>' %d[k]#.decode('utf-8')
            if k=='Year':
                sep=''
            ref=ref+d[k]+sep

    if d.has_key('URL'):
        print '''
            <br/>DOI: <a href="%s">%s</a><br/>
            Ref: %s<br/>
            <br>
            CODE at <a href="https://github.com/restrepo/webpy">GitHub</a>: doi.py<br/><br/>
        ''' %(d['URL'],d['URL'],ref) #.encode('utf-8'))
        print '''Official search at <a href="http://www.crossref.org/guestquery/#textsearch">crossref</a><br/>
        or <a href="http://search.crossref.org/">Search Crossref</a><br/>'''
    else:
        print '<br/>DOI lookup failed: try in <a href="http://search.crossref.org/">Crossref</a><br/>'
    