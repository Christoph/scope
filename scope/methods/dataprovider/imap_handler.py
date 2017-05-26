import imaplib
import email
from langdetect import detect
from email.utils import getaddresses
from email.header import decode_header
from urllib.parse import urlparse
from datetime import date, timedelta
from newspaper import Article
from . import url_extractor

from scope.methods.filters import blacklist_filter, remove_duplicate_articles_from_same_newsletter
from scope.methods.dataprovider import news_handler
from scope.models import Newsletter


class ImapHandler(object):
    """docstring for ImapHandler."""

    def __init__(self, agent, language):
        self.url_extractor = url_extractor.Extractor()
        self.mail_user = agent.user
        self.mail_pwd = agent.pwd
        self.mail_link = agent.imap
        self.mail_box = agent.mailbox
        self.mail_interval = agent.interval
        self.language = language

        self.news = news_handler.NewsSourceHandler()

    def get_data_new(self):
        items = self._connect()
        url_dict = []
        # Get the whole mail content
        for emailid in items:
            url_dict.append(self._fetch_urls_from_mail(emailid))
            # try:
            # fetching the mail, "`(RFC822)`" means "get the whole stuff",
            # but you can ask for headers only, etc

        # at this point it may be that we had several mails from the same
        # newsletter. In this step we merge the corresponding items so that in
        # the later steps we don't treat the same newsletter as different ones
        url_dict = self._merge_mails_from_same_newsletter(url_dict)

        downloaded_article_dict = self.news.get_articles_from_list(
            url_dict, self.language)
        # in case the same urls pointed to the same article (in sense of its title)
        filtered_article_dict = remove_duplicate_articles_from_same_newsletter(
            downloaded_article_dict)
        blacklist_filtered = blacklist_filter(filtered_article_dict)
        out = self.news.produce_output_dict(blacklist_filtered)

        language_filtered = []
        lang_dict = {
            'ger': 'de',
            'eng': 'en',
        }

        for a in out:
            if detect(a['body']) == lang_dict[self.language]:
                language_filtered.append(a)
            else:
                print("Wrong Language")
                print(a["title"])

        return language_filtered

    def _connect(self):
        # Connect to Mailbox
        self.mailbox = imaplib.IMAP4_SSL(self.mail_link)

        self.mailbox.login(self.mail_user, self.mail_pwd)
        self.mailbox.select("\""+self.mail_box+"\"")

        # Get all mails from the last interval hours
        if date.today().strftime('%w') == "1":
            yesterday = date.today() - timedelta(hours=self.mail_interval) - timedelta(days=2)
        else:
            yesterday = date.today() - timedelta(hours=self.mail_interval)

        # you could filter using the IMAP rules here (check
        # http://www.example-code.com/csharp/imap-search-critera.asp)
        resp, items = self.mailbox.search(
            None, '(SINCE "' + yesterday.strftime("%d-%b-%Y") + '")')
        items = items[0].split()  # getting the mails ids
        return items

    def _fetch_urls_from_mail(self, emailid):
        resp, data = self.mailbox.fetch(emailid, "(RFC822)")

        email_body = data[0][1]  # getting the mail content

        # Convert to mail object
        mail = email.message_from_string(email_body.decode("utf-8"))
        # All mail text/plain contents
        contents = self._get_content(mail)

        out_urls = []
        # Add urls from each content
        for content in contents:
            all_urls = self.url_extractor.get_urls_from_string(content)
            # remove exact duplicate from urls
            out_urls.extend(all_urls)

        newsletter, created = self._extract_newsletter(mail)

        return [list(set(out_urls)), newsletter]

    def _merge_mails_from_same_newsletter(self, url_dict):
    	newsletters = [newsletter for urls, newsletter in url_dict]
    	#single newsletters
    	newsletters = list(set(newsletters))
    	new_url_dict = []
    	for newsletter in newsletters:
    		interim = []
    		for urls, nl in url_dict:
    			if newsletter == nl:
    				interim.extend(urls)

    		new_url_dict.append([list(set(interim)), newsletter])

    	return new_url_dict


    def _extract_newsletter(self, mail):
       	# extract information about newsletter and create db-object
        try:
            sender = getaddresses(mail.get_all('from', []))[0]
            newsletter_mail = sender[1]
            newsletter_name = decode_header(sender[0])[0][0]
        except:
            newsletter_mail = "Unknown"
            newsletter_name = "Unknown"

        print(newsletter_name, newsletter_mail)
        newsletter, created = Newsletter.objects.get_or_create(
            email=newsletter_mail, defaults={"name": newsletter_name.title()})
        return newsletter, created


    def _get_content(self, mail):
        contents = []

        if mail.is_multipart():
            # Walk over all parts
            for part in mail.walk():
                self._get_decoding(contents, part)
        else:
            self._get_decoding(contents, mail)

        return contents

    def _get_decoding(self, contents, part):
        # Get content type
        ctype = part.get_content_type()
        # Get content encoding
        cenc = str(part.get('Content-Transfer-Encoding'))

        # Check if its text/plain and not text/html or multipart
        if ctype == 'text/plain':
            if cenc == 'quoted-printable':
                print("is MIME encoded")
                # If MIME encoded - decode and add
                contents.append(part.get_payload(decode=True).decode("utf-8"))
            elif cenc == 'base64':
                print("is base64 encoded")
                contents.append(part.get_payload(decode=True).decode("utf-8"))
            else:
                print("is not MIME encoded")
                # Else - add without decoding
                contents.append(part.get_payload())
