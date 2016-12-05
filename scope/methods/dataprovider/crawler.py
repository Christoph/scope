import re
import imaplib
import urllib2
import email
import quopri
from newspaper import Article
from urlparse import urlparse
from datetime import date, timedelta
from . import constants


class Crawler(object):
    """docstring for crawler."""

    def __init__(self, datasource):
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

        out = []

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

        # Get the whole mail content
        for emailid in items:
            # fetching the mail, "`(RFC822)`" means "get the whole stuff",
            # but you can ask for headers only, etc
            resp, data = mailbox.fetch(emailid, "(RFC822)")

            email_body = data[0][1]  # getting the mail content

            # Convert to mail object
            mail = email.message_from_string(quopri.decodestring(email_body))

            # Get mail payload
            if mail.is_multipart():
                content = mail.get_payload()[0].get_payload()

            else:
                content = mail.get_payload()

            # list set to remove duplicates
            # Still problems with links like:
            # http://www.cinemablend.com/news/1595010/why-jason-momoa-relates-so-closely-to-aquaman
            urls = set(list(re.findall(
                'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)))

            # Get real article urls
            for url in urls:
                try:
                    url = url.rstrip(')')
                    req = urllib2.Request(url)
                    res = urllib2.urlopen(req)
                    finalurl = res.geturl()
                    check_url = urlparse(finalurl)
                # TODO: Shoudnt catch all exceptions
                except:
                    print "error while checking url: " + url
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
                print "Error while downloading: " + a.url
                continue

        for article in articles:
            # and "tech" in article.text:
            # TODO: Problem: ")" will be added as article
            if article.title not in constants.EXCLUDE and \
               constants.UNSUBSCRIBE_EXCLUDE not in article.text:
                out.append({
                    "body": article.text, "title": article.title,
                    "url": article.url, "images": article.top_image,
                    "description": article.text[0:400] + "..."})

        return out
