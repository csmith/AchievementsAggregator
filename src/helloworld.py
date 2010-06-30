import cgi

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class User(db.Model):
    user = db.UserProperty()
    joindate = db.DateTimeProperty(auto_now_add=True)

class AchievementSource(db.Model):
    name = db.StringProperty()
    url = db.LinkProperty()

class UserAccount(db.Model):
    user = db.ReferenceProperty(reference_class=User)
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
    user = db.ReferenceProperty(reference_class=User)
    awarded = db.DateTimeProperty()
    discovered = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        self.show_header()

        if users.is_current_user_admin():
            self.show_admin_form()

        self.show_footer()

    def show_header(self):
        self.response.out.write("""
          <html>
            <head>
              <title>Achievements Aggregator</title>
            </head>
            <body>""")

    def show_footer(self):
        self.response.out.write("""
            </body>
          </html>""")

    def show_admin_form(self):
        self.response.out.write("""
          ADMIN!""")


class Guestbook(webapp.RequestHandler):
    def post(self):
        self.response.out.write('<html><body>You wrote:<pre>')
        self.response.out.write(cgi.escape(self.request.get('content')))
        self.response.out.write('</pre></body></html>')

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/sign', Guestbook)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()