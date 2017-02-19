import imaplib
import email
import quopri
import urllib2
from urlparse import urlparse
from datetime import date, timedelta
from newspaper import Article
from . import constants
from . import url_extractor

from scope.methods.dataprovider import news_handler


class ImapHandler(object):
    """docstring for ImapHandler."""

    def __init__(self, agent, language):
        self.url_extractor = url_extractor.Extractor()
        self.mail_user = agent.user.encode("utf-8")
        self.mail_pwd = agent.pwd.encode("utf-8")
        self.mail_link = agent.imap.encode("utf-8")
        self.mail_box = agent.mailbox.encode("utf-8")
        self.mail_interval = agent.interval
        self.language = language

        self.news = news_handler.NewsSourceHandler()

    # def get_data(self):
    #     out = []
    #
    #     # Connect to Mailbox
    #     mailbox = imaplib.IMAP4_SSL(self.mail_link)
    #     mailbox.login(self.mail_user, self.mail_pwd)
    #     mailbox.select(self.mail_box)
    #
    #     # Get all mails from the last interval hours
    #     yesterday = date.today() - timedelta(hours=self.mail_interval)
    #
    #     # you could filter using the IMAP rules here (check
    #     # http://www.example-code.com/csharp/imap-search-critera.asp)
    #     resp, items = mailbox.search(None, '(SINCE "' + yesterday.strftime("%d-%b-%Y") + '")')
    #     items = items[0].split()  # getting the mails ids
    #
    #     all_urls = []
    #     all_urls2 = []
    #
    #     # Get the whole mail content
    #     for emailid in items:
    #         # fetching the mail, "`(RFC822)`" means "get the whole stuff",
    #         # but you can ask for headers only, etc
    #         resp, data = mailbox.fetch(emailid, "(RFC822)")
    #
    #         email_body = data[0][1]  # getting the mail content
    #
    #         # Convert to mail object
    #
    #         mail = email.message_from_string(email_body)
    #         mail2 = email.message_from_string(quopri.decodestring(email_body))
    #
    #         # Get mail payload
    #         if mail.is_multipart():
    #             print "multipart"
    #             content = mail.get_payload()[0].get_payload()
    #             content2 = mail2.get_payload()[0].get_payload()
    #         else:
    #             print "single part"
    #             content = mail.get_payload()
    #             content2 = mail2.get_payload()[0].get_payload()
    #
    #         urls = self.url_extractor.get_urls_from_string(content)
    #         urls2 = self.url_extractor.get_urls_from_string(content2)
    #
    #         all_urls.extend(urls)
    #         all_urls2.extend(urls2)
    #
    #     # Remove duplicates over different newsletters
    #     all_urls = list(set(all_urls))
    #     all_urls2 = list(set(all_urls2))
    #     articles = []
    #     newspaper_lang_dict = {
    #         'ger': 'de',
    #         'eng': 'en',
    #     }
    #
    #     for i in range(0, len(all_urls)):
    #         try:
    #             if self.language == "mix":
    #                 articles.append(Article(all_urls[i]))
    #             else:
    #                 articles.append(Article(all_urls[i], language=newspaper_lang_dict[self.language]))
    #         except:
    #             try:
    #                 if self.language == "mix":
    #                     articles.append(Article(all_urls2[i]))
    #                 else:
    #                     articles.append(Article(all_urls2[i], language=newspaper_lang_dict[self.language]))
    #             except Exception as ex:
    #                 print ex
    #                 print "Error while  converting " + all_urls[i]
    #                 continue
    #             continue
    #
    #     # Download all articles
    #     for a in articles:
    #         try:
    #             a.download()
    #             a.parse()
    #         except:
    #             print "Error while downloading: " + a.url
    #             continue
    #
    #     print "Articles downloaded and parsed"
    #
    #     print "Article filter"
    #     for article in articles:
    #         if article.title not in constants.EXCLUDE and \
    #            constants.TITLE_BLACKLIST not in article.title and \
    #            constants.UNSUBSCRIBE_EXCLUDE not in article.text:
    #             out.append({
    #                 "body": article.text, "title": article.title,
    #                 "url": article.url, "images": article.top_image,
    #                 "source": urlparse(article.url).netloc,
    #                 "pubdate": article.publish_date})
    #         else:
    #             print article.title
    #             print article.url
    #
    #     return out

    def get_data_new(self):
        out = []

        # Connect to Mailbox
        mailbox = imaplib.IMAP4_SSL(self.mail_link)
        mailbox.login(self.mail_user, self.mail_pwd)
        mailbox.select(self.mail_box)

        # Get all mails from the last interval hours
        if date.today().strftime('%w') == "1":
            yesterday = date.today() - timedelta(hours=self.mail_interval) - timedelta(days=2)
        else:
            yesterday = date.today() - timedelta(hours=self.mail_interval)

        # you could filter using the IMAP rules here (check
        # http://www.example-code.com/csharp/imap-search-critera.asp)
        resp, items = mailbox.search(
            None, '(SINCE "' + yesterday.strftime("%d-%b-%Y") + '")')
        items = items[0].split()  # getting the mails ids

        all_urls = []

        # Get the whole mail content
        for emailid in items:
            try:
            # fetching the mail, "`(RFC822)`" means "get the whole stuff",
            # but you can ask for headers only, etc
                resp, data = mailbox.fetch(emailid, "(RFC822)")

                email_body = data[0][1]  # getting the mail content

                # Convert to mail object

                mail = email.message_from_string(email_body)

                # All mail text/plain contents
                contents = self._get_content(mail)

                # Add urls from each content
                for content in contents:
                    all_urls.extend(
                        self.url_extractor.get_urls_from_string(content))
            except:
                pass
        # Remove duplicates over different newsletters
        all_urls = list(set(all_urls))

        articles = self.news.get_articles_from_list(all_urls, self.language)

        for article in articles:
            if article.title not in constants.EXCLUDE and not self._blacklist_comparison(constants.TITLE_BLACKLIST, article.title) and not self._blacklist_comparison(constants.TEXT_BLACKLIST, article.text) and len(article.text) > 0:
                out.append({
                    "body": article.text, "title": article.title,
                    "url": article.url, "images": article.top_image,
                    "source": urlparse(article.url).netloc,
                    "pubdate": article.publish_date})
            else:
                print "Filtered"
                print article.title

        return out

    def _get_content(self, mail):
        contents = []

        if mail.is_multipart():
            # Walk over all parts
            for part in mail.walk():
                self._get_decoding(contents, part)
        else:
            self._get_decoding(contents, mail)

        return contents

    def _blacklist_comparison(self, blacklist, text):
        for item in blacklist:
            if text.find(item) >= 0:
                # print "Blacklisted"
                # print text
                return True
            else:
                return False

    def _get_decoding(self, contents, part):
        # Get content type
        ctype = part.get_content_type()
        # Get content encoding
        cenc = str(part.get('Content-Transfer-Encoding'))

        # Check if its text/plain and not text/html or multipart
        if ctype == 'text/plain':
            if cenc == 'quoted-printable':
                print "is MIME encoded"
                # If MIME encoded - decode and add
                contents.append(part.get_payload(decode=True))
            elif cenc == 'base64':
                print "is base64 encoded"
                contents.append(part.get_payload(decode=True))
            else:
                print "is not MIME encoded"
                # Else - add without decoding
                contents.append(part.get_payload())

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
            urls = list(set([i.split('"')[0].replace("=", "").replace(
                "3D", "=") for i in email_body.replace("\r\n", "").split('href=3D"') if i[0:4] == 'http']))
            no_urls = no_urls + len(urls)
            # parsing the mail content to get a mail object
            mail = email.message_from_string(email_body)
            sender, encoding = email.Header.decode_header(
                email.utils.parseaddr(mail.get('from'))[0])[0]
            senders_list.append(sender)
            # senders + sender + '<br/>'
            # senders = '<br/>'.join(list(set(senders_list)))
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
                    "source": urlparse(article.url).netloc,
                    "pubdate": article.publish_date})

        return out
