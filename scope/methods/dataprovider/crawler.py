import json
import imaplib
import urllib2
from newspaper import Article
from urlparse import urlparse
from datetime import date, timedelta
from . import constants


class Crawler(object):
    """docstring for crawler."""

    def __init__(self, datasource):
        if datasource == "json":
            self.datasource = self._load_JSON
        if datasource == "imap":
            self.datasource = self._load_imap

    def query_source(self, user):
        return self.datasource(user)

    def _load_imap(self, user):

        # Temporary customer imap data
        # mail_user = "enews@neulandherzer.net"
        # mail_pwd = "Ensemble_Enema"
        # mail_link = "imap.1und1.de"
        # mail_box = "INBOX"

        mail_user = "renesnewsletter"
        mail_pwd = "renewilllesen"
        mail_link = "imap.gmail.com"
        mail_box = "[Gmail]/All Mail"
        mail_interval = 24

        # Connect to Mailbox
        mailbox = imaplib.IMAP4_SSL(mail_link)
        mailbox.login(mail_user, mail_pwd)
        mailbox.select(mail_box)

        # Get all mails from the last interval hours
        yesterday = date.today() - timedelta(hours=mail_interval)

        # you could filter using the IMAP rules here (check
        # http://www.example-code.com/csharp/imap-search-critera.asp)
        resp, items = mailbox.search(
            None, '(SINCE "' + yesterday.strftime("%d-%b-%Y") + '")')
        items = items[0].split()  # getting the mails ids

        # TODO: Debug print message
        print items

        all_urls = []
        no_urls = 0

        # Get the whole mail content
        for emailid in items:
            # fetching the mail, "`(RFC822)`" means "get the whole stuff",
            # but you can ask for headers only, etc
            resp, data = mailbox.fetch(emailid, "(RFC822)")

            email_body = data[0][1]  # getting the mail content

            # TODO: Not sure what this does. Getting all in mail URLS?
            # Here are three regex from stackoverflow and the internet for that
            # (http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?
            # \b(https?|ftp|file)://[-A-Z0-9+&@#/%?=~_|!:,.;]*[A-Z0-9+&@#/%=~_|]
            # \b(?:(?:https?|ftp|file)://|www\.|ftp\.)
            #   (?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.])*
            #   (?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$])
            urls = list(set([i.split('"')[0].replace("=", "")
                             .replace("3D", "=")
                             for i in email_body.replace("\r\n", "")
                             .split('href=3D"') if i[0:4] == 'http']))

            no_urls = no_urls + len(urls)

            # Get real article urls
            for url in urls:
                try:
                    req = urllib2.Request(url)
                    res = urllib2.urlopen(req)
                    finalurl = res.geturl()
                    check_url = urlparse(finalurl)
                # TODO: Shoudnt catch all exceptions
                except:
                    print "error while checking url: "+url
                    continue

                test_list = []

                for x in constants.SUBSCRIBED_URLS:
                    if x in finalurl:
                        test_list.append("yes")
                if len(test_list) == 0 and (check_url.path != '/' and
                                            check_url.path != '' and
                                            check_url.path != '/en/'):
                    all_urls.append(finalurl)

        articles = [Article(x) for x in list(set(all_urls))]

        print "download"
        # Download alls articles
        for a in articles:
            try:
                a.download()
                a.parse()
            except:
                print "Error while downloading: "+a.url
                continue

        for article in articles:
            # and "tech" in article.text:
            if article.title not in constants.EXCLUDE and constants.UNSUBSCRIBE_EXCLUDE not in article.text:
                data.append({
                    "body": article.text, "title": article.title,
                    "url": article.url, "images": article.top_image,
                    "description": article.text[0:400] + "..."})

        return data

    def _load_JSON(self, user):
        # Load JSON
        raw = json.loads(
            open(user).read())

        # Get data
        data = [doc for doc in raw if
                (doc['title'] not in constants.EXCLUDE and
                    constants.UNSUBSCRIBE_EXCLUDE not in
                    doc['body'] and doc['isDuplicate'] is False)]

        return data
