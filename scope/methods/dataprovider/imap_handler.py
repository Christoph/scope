import imaplib
import email
from email.utils import getaddresses
from email.header import decode_header
from urlparse import urlparse
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
		self.mail_user = agent.user.encode("utf-8")
		self.mail_pwd = agent.pwd.encode("utf-8")
		self.mail_link = agent.imap.encode("utf-8")
		self.mail_box = agent.mailbox.encode("utf-8")
		self.mail_interval = agent.interval
		self.language = language

		self.news = news_handler.NewsSourceHandler()


	def get_data_new(self):
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

		article_dict = []

		# Get the whole mail content
		for emailid in items:
			# try:
			# fetching the mail, "`(RFC822)`" means "get the whole stuff",
			# but you can ask for headers only, etc
			resp, data = mailbox.fetch(emailid, "(RFC822)")

			email_body = data[0][1]  # getting the mail content

			# Convert to mail object
			mail = email.message_from_string(email_body)

			# extract information about newsletter and create db-object
			try:
				sender = getaddresses(mail.get_all('from', []))[0]
				newsletter_mail = sender[1]
				newsletter_name = decode_header(sender[0])[0][0]
			except:
				newsletter_mail = "Unknown"
				newsletter_name = "Unknown"

			print newsletter_name, newsletter_mail
			newsletter, created = Newsletter.objects.get_or_create(
				email=newsletter_mail, defaults={"name": newsletter_name.title()})
			# All mail text/plain contents
			contents = self._get_content(mail)

			# Add urls from each content
			for content in contents:
				all_urls = self.url_extractor.get_urls_from_string(content)
				#remove exact duplicate from urls 
				all_urls = list(set(all_urls))
				article_dict.append(
					[all_urls, newsletter])

		downloaded_article_dict = self.news.get_articles_from_list(
			article_dict, self.language)
		filtered_article_dict = remove_duplicate_articles_from_same_newsletter(downloaded_article_dict)
		blacklist_filtered = blacklist_filter(filtered_article_dict)
		out = []
		for articles, newsletter in blacklist_filtered:
			out.append([{
						"body": article.text, "title": article.title,
						"url": article.url, "images": article.top_image,
						"source": urlparse(article.url).netloc,
						"pubdate": article.publish_date,
						"newsletter": newsletter} for article in articles])

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
