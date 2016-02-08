#!/usr/bin/env python
'''
Search doi by title and fist author surname
    based on https://github.com/torfbolt/DOI-finder
    See: http://www.crossref.org/guestquery/#textsearch
'''
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
    
    title = re.sub(r"\$.*?\$","",title) # better remove all math expressions
    title = re.sub(r"[^a-zA-Z0-9 ]", " ", title) #remove non standard characters
    surname = re.sub(r"[{}'\\]","", surname) #remove non standard characters

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
    
        
    
    