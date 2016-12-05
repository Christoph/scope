from newspaper import Article as Art_News

import sys
import email
import imaplib
import urllib2
import json
from datetime import date, timedelta
from urlparse import urlparse


# from curate.models import Select
reload(sys)
sys.setdefaultencoding('utf8')


# user="enews@neulandherzer.net"
# pwd = "Ensemble_Enema"
# m = imaplib.IMAP4_SSL("imap.1und1.de")
# m.login(user,pwd)
# m.select("INBOX")

user = "renesnewsletter"
pwd = "renewilllesen"
# connecting to the gmail imap server
m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user, pwd)
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
            # print finalurl
        except:
            continue
        # somehow just using all(x not in finalurl for x in subscribed_urls)
        # the django shell doesn't manage
        test_list = []
        for x in subscribed_urls:
            if x in finalurl:
                test_list.append("yes")
        if len(test_list) == 0 and (check_url.path != '/' and check_url.path != '' and check_url.path != '/en/'):
            all_urls.append(finalurl)

np_articles = [Art_News(x) for x in list(set(all_urls))]

for a in np_articles:
    try:
        a.download()
        a.parse()
    except:
        pass

exclude = set(('', 'FT.com / Registration / Sign-up', 'Error', '404 Page not found',
               'Page no longer available', 'File or directory not found', 'Page not found', 'Content not found'))

unsubscribe_exclude = "If you are not redirected automatically, please click the Unsubscribe button below"

data = []

for article in np_articles:
    try:
        if article.title not in exclude and unsubscribe_exclude not in article.text:
            data.append({
                "body": article.text, "title": article.title,
                "url": article.url, "image": article.top_image,
                "description": article.text[0:400] + "..."})
    except:
        pass

with open('curate/data/data.json', 'w+') as fp:
    json.dump(data, fp)
