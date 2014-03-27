# Project Title
Local Magic

## Author
- Etan Ilfeld, 
- github account: ilfeld


## Description
Local Magic combines technological 'magic' with aesthetic 'alchemy.' The idea of this project is to generate a visually enticing and informative webpage based on the input of any address. The first stage of the project was to write a script in python that uses the Wikipedia API and finds Wikipedia articles that have a GPS coordinate within a given radius. The second stage was to use Google's Geocoding API to find a GPS coordiante (longitude and lattitude) that matches a given address. The third stage invovled writing a script that lookups the amount of visitor views for Wikipedia articles via stats.grok.se and finally, by synthesizing these elements on Google App Engine, we have a web app that takes an address as an input and outputs the GPS coordinates and most visited Wikipedia articles in that vicinity. 

The next step is to try and create an interesting and playfully artistic manner to represent the information and perhaps to add some more data, which can also be visualized.

## Link to Prototype
[Prototype Link](http://local-magic.appspot.com "Prototype Link")

## Example Code
Note that this code was writting in Python and run on Google's App Engine
```
## Lookup viewing statistics for a Wikipedia Article       
def tcount(title):
    stats_website = "stats.grok.se/en/201312/" 
    q = stats_website+title
    #next line checks for errors if necessary in terms of non-ascii characters
    querystr='http://' + urllib.quote(q.encode('UTF-8'))
    try:
        resp = urlfetch.fetch(querystr, method=urlfetch.GET, deadline=10)
        recent = resp.content
    except urlfetch.DownloadError:
        print 'error'
    x= recent.index('times')
    y=recent.index('viewed')
    number= int(recent[y+7:x])
    return number
    
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
```
## Links to External Libraries
[Github Repository for Project](https://github.com/ilfeld/devart-template/ "Github")

## Images & Videos
![Example Image](project_images/cover.png?raw=true "Example Image")
