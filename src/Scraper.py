from BeautifulSoup import BeautifulSoup
from datetime import datetime
import urllib2

class Scraper:

    @staticmethod
    def scrape_spore(credentials):
        results = []
        url = "http://www.spore.com/view/achievements/%s" % credentials
        fmt = "%a %B %d, %Y"

        try:
          result = urllib2.urlopen(url).read()
          soup = BeautifulSoup(result)
          achdiv = soup.find('h2', 'achievementsH2').findNextSibling('div', 'fields')

          for ach in achdiv.findAll('table'):
              results.append({'img': "http://www.spore.com%s" % ach.find('img')['src'],
                              'title': ach.find('b').string.strip(),
                              'desc': ach.find('div', 'achievementDesc').contents[0].strip(),
                              'date': datetime.strptime(ach.find('span').string.strip(), fmt)})
        except urllib2.URLError, e:
          handleError(e)

        return results
