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
          <h1>Sources</h1>
          <h2>Add</h2>
          <form action="/admin/addsource" method="post">
           <label>Name: <input type="text" name="name"/></label>
           <label>URL: <input type="text" name="url"/></label>
           <input type="submit" value="Add"/>
          </form>
          <h2>View</h2>
          <table>
           <tr><th>Source</th><th>URL</th></tr>
           """)

        for source in AchievementSource.all():
            self.response.out.write("<tr><td>");
            self.response.out.write(cgi.escape(source.name))
            self.response.out.write("</td><td>");
            self.response.out.write(cgi.escape(source.url))
            self.response.out.write("</td></tr>");

class AddSourcePage(webapp.RequestHandler):
    def post(self):

        if not users.is_current_user_admin():
            self.error(403)
            return

        source = AchievementSource(name=self.request.get('name'),
                                   url=self.request.get('url'))
        source.put()

        self.redirect('/')


class Guestbook(webapp.RequestHandler):
    def post(self):
        self.response.out.write('<html><body>You wrote:<pre>')
        self.response.out.write(cgi.escape(self.request.get('content')))
        self.response.out.write('</pre></body></html>')

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/sign', Guestbook),
                                      ('/admin/addsource', AddSourcePage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()