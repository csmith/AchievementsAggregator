import cgi
from Scraper import Scraper
import os
from google.appengine.ext.webapp import template

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class AchievementSource(db.Model):
    name = db.StringProperty()
    url = db.LinkProperty()

class UserAccount(db.Model):
    user = db.UserProperty()
    source = db.ReferenceProperty(reference_class=AchievementSource)
    credentials = db.StringProperty()
    added = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty()

class Achievement(db.Model):
    name = db.StringProperty()
    image = db.LinkProperty()
    description = db.StringProperty()
    source = db.ReferenceProperty(reference_class=AchievementSource)

class AwardedAchievement(db.Model):
    achievement = db.ReferenceProperty(reference_class=Achievement)
    user = db.UserProperty()
    awarded = db.DateTimeProperty()
    discovered = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        template_values = {
            'is_admin': users.is_current_user_admin(),
            'sources': AchievementSource.all(),
            'accounts': UserAccount.gql("WHERE user = :user", user=user),
            'achievements': AwardedAchievement.all().filter('user = ', user)
                                              .order('-awarded')
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

    def show_sources(self):
        self.response.out.write("</table>")
        self.response.out.write("""<h2>Add Account</h2>
          <form action="/addaccount" method="post">
           <label>Type: <select name="type">""")

        for source in AchievementSource.all():
            self.response.out.write('<option value="')
            self.response.out.write(source.key())
            self.response.out.write('">')
            self.response.out.write(cgi.escape(source.name))
            self.response.out.write('</option>')

        self.response.out.write("""</select></label>
           <label>Credentials: <input type="text" name="credentials"/></label>
           <input type="submit" value="Add"/>
          </form>""")

class AddSourcePage(webapp.RequestHandler):
    def post(self):

        if not users.is_current_user_admin():
            self.error(403)
            return

        source = AchievementSource(name=self.request.get('name'),
                                   url=self.request.get('url'))
        source.put()

        self.redirect('/')

class AddAccountPage(webapp.RequestHandler):
    def post(self):

        if not users.get_current_user():
            self.error(403)
            return

        source = db.get(db.Key(self.request.get('type')))

        account = UserAccount(user=users.get_current_user(),
                              source=source,
                              credentials=self.request.get('credentials'))
        account.put()

        self.redirect('/')


class UpdatePage(webapp.RequestHandler):

    def post(self):
        account = db.get(db.Key(self.request.get('key')))
        res = []

        if account.source.name == 'Spore':
            res = Scraper.scrape_spore(account.credentials)

        UpdatePage.merge_achievements(account, res)

    @staticmethod
    def merge_achievements(account, achievements):
        for awarded in achievements:
            achievement = UpdatePage.get_achievement(account.source, awarded)

            res = AwardedAchievement.gql("WHERE achievement = :ac AND user = :user",
                                         ac=achievement,
                                         user=account.user)

            if res.count(1) == 0:
                AwardedAchievement(achievement=achievement,
                                   user=account.user,
                                   awarded=awarded['date']).put()

    @staticmethod
    def get_achievement(source, achievement):
        res = Achievement.gql("WHERE name = :name AND source = :source",
                              name=achievement['title'],
                              source=source)

        if res.count(1) == 0:
            res = Achievement(name=achievement['title'],
                              image=achievement['img'],
                              description=achievement['desc'],
                              source=source)
            res.put()
        else:
            res = res.get()

        return res

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/admin/addsource', AddSourcePage),
                                      ('/worker/update', UpdatePage),
                                      ('/addaccount', AddAccountPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()