import imaplib
import email
import quopri
from urlparse import urlparse
from datetime import date, timedelta
from newspaper import Article
from . import constants
from . import url_extractor

reload(url_extractor)


class ImapHandler(object):
    """docstring for ImapHandler."""
    def __init__(self):
        self.url_extractor = url_extractor.Extractor()

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

            urls = self.url_extractor.get_urls_from_string(content)

            all_urls.extend(urls)

        articles = [Article(x) for x in list(set(all_urls))]

        # Download alls articles
        for a in articles:
            try:
                a.download()
                a.parse()
            except:
                print "Error while downloading: " + a.url
                continue

        for article in articles:
            if article.title not in constants.EXCLUDE and \
               constants.UNSUBSCRIBE_EXCLUDE not in article.text:
                out.append({
                    "body": article.text, "title": article.title,
                    "url": article.url, "images": article.top_image,
                    "source": urlparse(article.url).netloc})

        return out
