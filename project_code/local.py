import cgi
import urllib
import json
import re
import datetime
import ast
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2


MAIN_PAGE_HTML = """\
<!doctype html>
<html>
  <body>
    <form action="/sign" method="post">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Enter address to discover popular wikipedia pages in its vicinity"></div>
    </form>
  </body>
</html>
"""


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write(MAIN_PAGE_HTML)


class Guestbook(webapp2.RequestHandler):

    def post(self):
        self.response.write('</strong><a href="/">CLICK HERE TO TRY ANOTHER ADDRESS</a><br>')
        self.response.write('<!doctype html><html><body><br>You wrote: <i>"')
        self.response.write(cgi.escape(self.request.get('content'))+'"</i>')
        address=str(cgi.escape(self.request.get('content')))
        g=  addressToGPS(address)
        self.response.write('   The resulting longitude and lattitude are: <strong>%s   ' %g)
        self.response.write('</strong>Here are the most popular sites nearby (with their Wikipedia popularity determining their size)<br><strong>%s</body></html>' %GetWiki(g))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)



##Convert Address to GPS coordinate
def addressToGPS(address):
## e.g.   address="98 st martins lane+london+uk"
    query="https://maps.googleapis.com/maps/api/geocode/json?address="+address+"&sensor=false&key=AIzaSyD63W8pJdthlFCNg_r3sSLOQrMW8exrcX4"

    p=urllib.urlopen(query).read()

    g= (json.loads(p))
    if g['status'] != "ZERO_RESULTS":
        gps= [g['results'][0]['geometry']['location']['lat'],g['results'][0]['geometry']['location']['lng']]
        return str(gps)
    else:
        return "Zero results were found for address"
    
       
def tcount(title):
    stats_website = "stats.grok.se/en/201312/" 
    q = stats_website+title
    #next line checks for errors if necessary in terms of non-ascii characters
##    print q, type(q), q.encode('UTF-8')
    querystr='http://' + urllib.quote(q.encode('UTF-8'))
##    print querystr
##    recent=urllib.urlopen(querystr).read()

    try:
        resp = urlfetch.fetch(querystr, method=urlfetch.GET, deadline=10)
        recent = resp.content
    except urlfetch.DownloadError:
        print 'error'
    
    x= recent.index('times')
    y=recent.index('viewed')
    number= int(recent[y+7:x])
    return number
##    return json.loads(recent)['daily_views'].get(recent_popularity)    



##Get Stats for Wikisearch
def GetWiki(gps):
    gps=ast.literal_eval(gps)
    lattitude=str(gps[0])
    longitude=str(gps[1])
    website="http://en.wikipedia.org/w/api.php"
    query="?action=query&format=json&generator="
    limit="limit=12"
    ##gps=[ 32.070278, 34.794167] Electra Tower
    radius="9000"
    location="geosearch&ggscoord="+lattitude+"%7C"+longitude+"&ggsradius="+radius+"&ggs"
    images_query = 'https://en.wikipedia.org/w/api.php?action=query&prop=images&format=json&pageids='
    TOP_COUNT = 7
    full=website+query+location+limit
    near_pages=urllib.urlopen(full).read()
    res = json.loads(near_pages)
    if res is None or len(res) == 0 or res == '':
        return 'No results found'
    else:
        p=res.get('query', {}).get('pages')
        if p is None:
            return 'No results found this time'+str(res)+str(gps)+longitude
        ordered=""
        size=7
        final_pages = {}
        pages_scores = {}
        listpages=[]
        statlist=[]
        for page_id, page in p.iteritems():
            # Get the page's popularity and normalize it
            stat=tcount(page['title'])
            normalized=round((stat)/2000)
            if normalized >15:
                normalized=15
            if normalized < 1:
                normalized=1
            pages_scores[page_id] = [page['title'], normalized]
            listpages.append([page['title'],page_id,stat])
            statlist.append(stat)
        avgstat=sum(statlist)/len(statlist)
        minim=min(statlist)
        maxim=max(statlist)
        second=avgstat-minim
        beforelast=maxim-avgstat
        s=5
        for x in listpages:
            pageStat=x[2]
            if pageStat>maxim-10:
                s=10
            else:
                if pageStat<minim+10:
                    s=1
                else:
                    if pageStat>minim and pageStat<avgstat:
                        s=5
                    else:
                        if pageStat>avgstat and pageStat<maxim:
                            s=8
                        else:
                            if pageStat==avgstat:
                                s=7
            url="http://en.wikipedia.org/wiki?curid="+str(x[1])
            ordered= ordered+"<font size='"+str(s)+"'><a href="+"'"+url+"'"+'>'+str(x[0])+"</a>  </font>"
        for x in range(0,7):
            ordered=ordered+ordered
        return ordered


##        sorted_scores = sorted(pages_scores.items(), key=lambda e: e[1][1], reverse=True)[:TOP_COUNT]
##        res = dict(sorted_scores)
##        for k in res.keys():
##            res[k] = res[k][0]
##
##        ordered="</strong><font size='4'>The most popular sites nearby (with popularity determining size)<br> </font><strong>"
##        size=7
##        for k in res:
##            ordered= ordered+"<font size='"+str(size)+"'>"+res[k]+". </font>"
##            size=size-1
##        return ordered+str(sorted_scores)
    





