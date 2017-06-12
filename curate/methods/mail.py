import configparser
from django.core.mail import send_mail
from scope.methods.auxiliary.auxiliaryfunctions import truncate_words_and_prod_sentence
from django.template.loader import render_to_string
from curate.models import Curate_Query, Curate_Customer, Curate_Recipient
from scope.models import Customer
from django.conf import settings
from django.core.urlresolvers import reverse
from curate.convenience.functions import retrieve_objects


def send_newsletter(customer_key):
    customer, curate_customer = retrieve_objects(customer_key)
    query = Curate_Query.objects.filter(
        curate_customer=curate_customer).order_by("pk").last()
    config = configparser.RawConfigParser()
    config.read('curate/customers/' + customer_key +
                "/" + customer_key + '.cfg')

    recipients = Curate_Recipient.objects.filter(
        curate_customer=curate_customer)
    template_no = config.getint('outlet', 'mail_template_no')

    # if config.get('outlet', 'options') == 'all':
    # 	selection_options = Curate_Customer_Selection.objects.filter(
    # 		curate_customer=curate_customer).filter(kind="sel").all()
    # else:
    # 	names = config.get('outlet', 'options').split(',')
    # 	selection_options = Curate_Customer_Selection.objects.filter(
    # 		curate_customer=curate_customer).filter(name__in=names).all()

    # send_dict = {}
    # for option in selection_options:
    # 	articles = [i.article for i in Article_Curate_Query.objects.filter(curate_query=query).filter(
    # 		selection_options=option).order_by("rank").all()]
    # 	send_dict[option.name] = articles

    instances = query.selected_articles()
    articles = [i.article for i in instances]
    ma = min(3, len(instances))
    keywords = []
    for i in instances[:ma]:
        try:
            keywords.append(i.center.filter(center__curate_query=query).first(
    ).keywords)
        except:
            pass

    send_dict = {'sel': articles}

    stats_dict = {'words': query.processed_words,
                  'no_of_articles': query.articles_before_filtering}

    for recipient in recipients:
        send_mail(
            subject="Scope Neu: " + "; ".join(keywords),
            message=mail_template(stats_dict, articles, query,
                                  template_no, html=False, recipient_name=recipient.first),
            from_email='robot@scope.ai',
            recipient_list=[recipient.email],
            html_message=mail_template(
                stats_dict, send_dict, query, template_no, recipient_name=recipient.first)
        )


def mail_template(stats_dict, send_dict, query, no, html=True, recipient_name=""):
    if no == 1:
        if html == True:
            content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html xmlns="http://www.w3.org/1999/xhtml"> <head> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> <title>NewsButler brief</title> <meta name="viewport" content="width=device-width, initial-scale=1.0"/> </head> <body style="margin: 0; padding: 0; font-family: Times New Roman, sans-serif;"> <table align="center" border="0" style="border-bottom:0px; border-top:0px; border-color:#588B8B;" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse;"> <!-- Header --> <tr> <td align="center" bgcolor="#588B8B" style="padding: 40px 0 30px 0;"><h1 style="font-family:Times New Roman, sans-serif;"></h1></td> </tr><tr><td align="center" bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;"><h2 style="font-family:Times New Roman, sans-serif;">This is your Scope newsletter for ' + \
                query.time_stamp.strftime("%a %d/%m %Y") + \
                '. Enjoy!</h2><br/><hr align="center" width="80%" style="color:#588B8B;border-color: #588B8B;border:2px solid;"></tr>'
            for item in list(send_dict.items()):
                # content = content + '<tr border="1px solid #588B8B"
                # style="width:80%;"><td bgcolor="#588B8B" style="color:#fff;
                # text-align:center;"><br/><h3><strong> Selection option "' +
                # str(item[0]) + '": </strong></h3><br/></td> </tr>'
                articles = item[1]
                for j in range(0, len(articles)):
                    article = articles[j]
                # <!-- Main -->
                    content = content + '<tr border-bottom="1px solid #588B8B"> <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;"> <table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td style="font-family:Times New Roman, sans-serif; font-size:16px;"><b>' + str(j + 1) + '.<a style="color: #2b2b2b; text-decoration:none;" href="' + str(article.url) + '"><font color="#2b2b2b">' + article.title + '</font></a> <br/><br/><font color="#2b2b2b" "text-decoration=none"> ' + article.source.url + '</font></b><br/><br/></td> </tr> <tr> <td style="font-family:Times New Roman, sans-serif; font-size:16px">' + truncate_words_and_prod_sentence(
                        article.body, 200) + '</td> </tr> <tr> <td> <table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td style="font-family:Times New Roman, sans-serif;" width="260" valign="top">' + article.keywords + '</td> <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td> <td width="260" valign="top"></td> </tr> </table> </td> </tr> </table><br/><br/><hr align="center" width="80%" style="color:#588B8B;border-color: #588B8B;border:2px solid;"></td> </tr>'

            content = content + '<tr> <td bgcolor="#588B8B" style="padding: 30px 30px 30px 30px;"> <table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td style="font-family:Times New Roman, sans-serif;" width="75%"> &copy; <a href="www.scope.ai">Scope</a> 2017<br/></td> <td> <td align="right"> <table border="0" cellpadding="0" cellspacing="0"> <tr> <td></td> <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td> <td></td> </tr> </table> </td> </td> </tr> </table> </td> </tr> </table> </body> </html> '
        else:
            content = "This mail can be displayed in html-compatible mail-viewers only. Sorry!"

    elif no == 2:
        if html == True:
            articles = []
            try:
                for key, value in list(send_dict.items()):
                    articles.extend(value)
            except:
                pass
            context = {"articles": articles, "stats_dict": stats_dict,
                       'recipient_name': recipient_name}
            content = render_to_string('curate/mail_template.html', context)
        else:
            content = "This mail can be displayed in html-compatible mail-viewers only. Sorry!"

    return content


def send_notification(customer_key, hot=False, cc=False):
    customer, curate_customer = retrieve_objects(customer_key)
    rec = []
    if hot:
        recipients = Curate_Recipient.objects.filter(
            curate_customer=curate_customer, is_editor=True).values('first', 'email')
        rec.extend(recipients)
    if cc:
        rec.append({'first': 'Admin', 'email': "admin@scope.ai"})
        # if len(cc) == 0:
        #     rec.append({'name':'Admin', 'email':"admin@scope.ai"})
        # else:
        #     for i in cc:
        #         rec.append({'name':'', 'email':i})

    url_interface = settings.CURRENT_DOMAIN + reverse('curate:interface')
    url_dashboard = settings.CURRENT_DOMAIN + reverse('curate:controlcenter:dashboard', kwargs={'pk': 0})
    url_contact = settings.CURRENT_DOMAIN + reverse('homepage:contact')
    for recipient in recipients:
        context = {'name': recipient['first'], 'url_interface': url_interface,
                   'url_dashboard': url_dashboard,'url_contact':url_contact, 'customer_name': customer.name}
        content = render_to_string(
            'curate/notification_template.html', context)
        send_mail('New Scope Pre-Selection available', 'Sorry, this service works only for html-compatible mail clients',
                  'robot@scope.ai', [recipient['email']], connection=None, html_message=content)
