#!/usr/bin/env python
'''
Search doi by title and fist author surname
    based on https://github.com/torfbolt/DOI-finder
    See: http://www.crossref.org/guestquery/#textsearch
'''
def searchdoi(title='a model of  leptons', surname='Weinberg'):
    import re
    import urllib
    from bs4 import BeautifulSoup
    import httplib
    
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
    title = re.sub(r"\$.*?\$","",title) # better remove all math expressions
    title = re.sub(r"[^a-zA-Z0-9 ]", " ", title) #remove non standard characters
    surname = re.sub(r"[{}'\\]","", surname) #remove non standard characters
    params = urllib.urlencode({"titlesearch":"titlesearch", "auth2" : surname, "atitle2" : title, "multi_hit" : "on", "article_title_search" : "Search", "queryType" : "author-title"})
    headers = {"User-Agent": "Mozilla/5.0" , "Accept": "text/html", "Content-Type" : "application/x-www-form-urlencoded", "Host" : "www.crossref.org"}
    conn = httplib.HTTPConnection("www.crossref.org:80")
    conn.request("POST", "/guestquery/", params, headers)
    response = conn.getresponse()
    # print response.status, response.reason
    data = response.read()
    conn.close()
    result = re.findall(r"\<table cellspacing=1 cellpadding=1 width=600 border=0\>.*?\<\/table\>" ,data, re.DOTALL)
    if (len(result) > 0):
        html=urllib.unquote_plus(result[0])
        #doi=re.sub('.*dx.doi.org\/(.*)<\/a>.*','\\1',doitmp)
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
            doi['ISSN']=re.sub('([a-zA-Z0-9]{4})([a-zA-Z0-9]{4})','\\1-\\2',doi['ISSN'])
            doi[u'DOI']=doi['Persistent Link']
            
    return doi

if __name__ == "__main__":
    import sys
    title='';first_author_surname=''
    if sys.argv[1]:
        title=sys.argv[1]
    if sys.argv[2]:
        first_author_surname=sys.argv[2]
        
    d=searchdoi(title,first_author_surname)
    ref='';sep=','
    for k in ['Author','Article Title','Journal Title','Volume','Issue','Page','Year']:
        if d.has_key(k):
            if k=='Volume':
                d[k]='<strong>%s</strong>' %d[k]
            if k=='Year':
                sep=''
            ref=ref+d[k]+sep

    if d.has_key('DOI'):
        print '''
            <br/>DOI: <a href="%s">%s</a><br/>
            Ref: %s<br/>
            <br>
            CODE at <a href="https://github.com/restrepo/webpy">GitHub</a>: doi.py<br/><br/>
        ''' %(d['DOI'],d['DOI'],ref)
        print 'Official search at <a href="http://www.crossref.org/guestquery/#textsearch">crossref</a>'
    else:
        print '<br/>DOI lookup failed: try in: <a href="http://www.crossref.org/guestquery/#textsearch">crossref</a>'
    
        
    
    