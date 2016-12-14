import imaplib
import email
import quopri
from urlparse import urlparse
from datetime import date, timedelta
from newspaper import Article
from . import constants
from . import url_extractor


class ImapHandler(object):
    """docstring for ImapHandler."""
    def __init__(self, agent):
        self.url_extractor = url_extractor.Extractor()
        self.mail_user = agent.user.encode("utf-8")
        self.mail_pwd = agent.pwd.encode("utf-8")
        self.mail_link = agent.imap.encode("utf-8")
        self.mail_box = agent.mailbox.encode("utf-8")
        self.mail_interval = agent.interval

    def get_data(self):

        out = []

        # Connect to Mailbox
        mailbox = imaplib.IMAP4_SSL(self.mail_link)
        mailbox.login(self.mail_user, self.mail_pwd)
        mailbox.select(self.mail_box)

        # Get all mails from the last interval hours
        yesterday = date.today() - timedelta(hours=self.mail_interval)

        # you could filter using the IMAP rules here (check
        # http://www.example-code.com/csharp/imap-search-critera.asp)
        resp, items = mailbox.search(
            None, '(SINCE "' + yesterday.strftime("%d-%b-%Y") + '")')
        items = items[0].split()  # getting the mails ids

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
                print "multipart"
                content = mail.get_payload()[0].get_payload()
            else:
                print "single part"
                content = mail.get_payload()

            urls = self.url_extractor.get_urls_from_string(content)

            all_urls.extend(urls)

        # Remove duplicates over different newsletters
        all_urls = list(set(all_urls))
        articles = []

        for url in all_urls:
            try:
                articles.append(Article(url))
            except:
                print "Error while  converting " + url
                continue

        # articles = [Article(x) for x in list(set(all_urls))]

        # Download all articles
        for a in articles:
            try:
                a.download()
                a.parse()
            except:
                print "Error while downloading: " + a.url
                continue

        print "Articles downloaded and parsed"

        for article in articles:
            if article.title not in constants.EXCLUDE and \
               constants.UNSUBSCRIBE_EXCLUDE not in article.text:
                out.append({
                    "body": article.text, "title": article.title,
                    "url": article.url, "images": article.top_image,
                    "source": urlparse(article.url).netloc})

        return out
