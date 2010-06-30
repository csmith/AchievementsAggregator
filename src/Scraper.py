from BeautifulSoup import BeautifulSoup
import urllib2

class scraper:

    def scrape_spore(self, credentials):
        results = []
        url = "http://www.spore.com/view/achievements/%s" % credentials
        try:
          result = urllib2.urlopen(url).read()
          soup = BeautifulSoup(result)
          achdiv = soup.find('h2', 'achievementsH2').findNextSibling('div', 'fields')

          for ach in achdiv.findAll('table'):
              img = "http://www.spore.com%s" % ach.find('img')['src']
              title = ach.find('b').string.strip()
              desc = ach.find('div', 'achievementDesc').contents[0].strip()
              date = ach.find('span').string.strip()
              results.append({'img': img, 'title': title, 'desc': desc, 'date': date})
        except urllib2.URLError, e:
          handleError(e)

        return results