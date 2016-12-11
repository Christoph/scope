import re
import imaplib
import urllib2
import email
import quopri
from newspaper import Article
from urlparse import urlparse
from datetime import date, timedelta
from . import constants


class ImapHandler(object):
    """docstring for ImapHandler."""

    def _get_urls_from_string(self, content):
        test_list = []
        urls_list = []

        # list set to remove duplicates
        # Still problems with links like:
        # http://www.cinemablend.com/news/1595010/why-jason-momoa-relates-so-closely-to-aquaman
        urls = set(list(re.findall(
            ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
             '(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            content)))

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

            # TODO: Not sure what is the use of this lines
            # Maybe creating a blacklist and not a whitelist?
            for x in constants.SUBSCRIBED_URLS:
                if x in finalurl:
                    test_list.append("yes")
            if len(test_list) == 0 and (check_url.path != '/' and
                                        check_url.path != '' and
                                        check_url.path != '/en/'):
                urls_list.append(finalurl)

            # urls_list.append(finalurl)

        return urls_list

    def get_data(self, source):
        mail_user = source.user.encode("utf-8")
        mail_pwd = source.pwd.encode("utf-8")
        mail_link = source.imap.encode("utf-8")
        mail_box = source.mailbox.encode("utf-8")
        mail_interval = source.interval

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

            urls = self._get_urls_from_string(content)

            all_urls.extend(urls)

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
                    "description": article.text[0:294] + "..."})

        return out
