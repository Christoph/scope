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

    def get_data_old(self):
        m = imaplib.IMAP4_SSL(self.mail_link)
        m.login(self.mail_user, self.mail_pwd)
        m.select(self.mail_box)

        # here you a can choose a mail box like INBOX instead
        m.select("[Gmail]/All Mail")

        yesterday = date.today() - timedelta(hours=24)

        # you could filter using the IMAP rules here (check
        # http://www.example-code.com/csharp/imap-search-critera.asp)
        resp, items = m.search(
            None, '(SINCE "' + yesterday.strftime("%d-%b-%Y") + '")')
        # at this step we want to download all the relevant mails since the last
        # newsletter. There should be filters for this.
        items = items[0].split()  # getting the mails id
        print items

        subscribed_urls = ["launch.us", "launch.co", "index.co", "azhar", "getrevue.co", "morningreader.com", "producthunt.com", "betalist", "crunchable", "mailchimp.com", "facebook.com", "twitter.com", "launchticker", "play.google.com", "www.technologyreview.com/newsletters",
                           "launchevents.typeform.com", "ev.inside.com", "itunes.apple.com", "https://www.technologyreview.com/?utm_source", "typeform", "producthunt.us3.list-manage.com", "getfeedback", "youtube.com", "forms/", "smashingmagazine", "wikipedia.org"]

        exclude = set(('', 'FT.com / Registration / Sign-up', 'Error', '404 Page not found',
                       'Page no longer available', 'File or directory not found', 'Page not found', 'Content not found'))

        unsubscribe_exclude = "If you are not redirected automatically, please click the Unsubscribe button below"

        all_urls = []
        no_urls = 0
        senders_list = []
        # for emailid in range(int(items[2]),int(items[2])+2):
        for emailid in items:
            # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can
            # ask for headers only, etc
            resp, data = m.fetch(emailid, "(RFC822)")
            email_body = data[0][1]  # getting the mail content
            # [i.split('"')[0].replace("=","").replace("click?upn3D","click?upn=") for i in email_body.replace("\r\n","").split('href=3D"') if i[0:4] == 'http']
            urls = list(set([i.split('"')[0].replace("=", "").replace("3D", "=")
                             for i in email_body.replace("\r\n", "").split('href=3D"') if i[0:4] == 'http']))
            no_urls = no_urls + len(urls)
            # parsing the mail content to get a mail object
            mail = email.message_from_string(email_body)
            sender, encoding = email.Header.decode_header(
                email.utils.parseaddr(mail.get('from'))[0])[0]
            senders_list.append(sender)
            # senders + sender + '<br/>'
            senders = '<br/>'.join(list(set(senders_list)))
            for url in urls:
                try:
                    req = urllib2.Request(url)
                    res = urllib2.urlopen(req)
                    finalurl = res.geturl()
                    check_url = urlparse(finalurl)
                    print finalurl
                except:
                    print "error while checking url: " + url
                    continue
                # somehow just using all(x not in finalurl for x in subscribed_urls)
                # the django shell doesn't manage
                test_list = []
                for x in subscribed_urls:
                    if x in finalurl:
                        test_list.append("yes")
                if len(test_list) == 0 and (check_url.path != '/' and check_url.path != '' and check_url.path != '/en/'):
                    all_urls.append(finalurl)
        articles = []

        for url in all_urls:
            try:
                articles.append(Article(url))
            except:
                print "Error while  converting " + url
                continue

        # Download all articles
        for a in articles:
            try:
                a.download()
                a.parse()
            except:
                print "Error while downloading: " + a.url
                continue

        print "Articles downloaded and parsed"

        out = []

        for article in articles:
            if article.title not in exclude and unsubscribe_exclude not in article.text:
                out.append({
                    "body": article.text, "title": article.title,
                    "url": article.url, "images": article.top_image,
                    "source": urlparse(article.url).netloc})

        return out
