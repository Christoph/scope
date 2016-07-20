import json
from networkx.readwrite import json_graph
from django.core.mail import send_mail
#from last24h.models import Suggest
from django.conf import settings
from datetime import date



data = json.loads(open('last24h/static/last24h/cs/cs_'+ strin +'_nl.json').read())
ug = json_graph.node_link_graph(data)
#<!-- Header -->
content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html xmlns="http://www.w3.org/1999/xhtml"> <head> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> <title>NewsButler brief</title> <meta name="viewport" content="width=device-width, initial-scale=1.0"/> </head> <body style="margin: 0; padding: 0; font-family: Times New Roman, sans-serif;"> <table align="center" border="0" style="border-bottom:0px; border-top:0px; border-color:#aec7e8;" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse;"> <!-- Header --> <tr> <td align="center" bgcolor="#aec7e8" style="padding: 40px 0 30px 0;"><h1 style="font-family:Times New Roman, sans-serif;"></h1></td> </tr><tr><td align="center" bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;"><h2 style="font-family:Times New Roman, sans-serif;">This is your NewsButler brief for ' + date.today().strftime("%a %d/%m %Y") + '. Enjoy!</h2><br/><strong>Today based on the following newsletters:<br/>'+ ug.graph['senders'] + '<br/><hr align="center" width="80%" style="color:#aec7e8;border-color: #aec7e8;border:2px solid;"></tr>'

#list = Suggest.objects.filter(custom = 'last24h').order_by('distance')
#list = sorted([[ug.node[i]['suggest'],ug.node[i]] for i in ug.nodes() if (0 < ug.node[i]['suggest'] <= 10) ])
max = ug.graph['comps']

#if len(list) == 0:
list = sorted([[ug.node[i]['suggest'],ug.node[i]] for i in ug.nodes() if (0 < ug.node[i]['suggest'] <= max) ])
	# <!-- Main -->
for i in list:
		# <!-- Main -->
		content = content + '<tr border-bottom="1px solid #aec7e8"> <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;"> <table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td style="font-family:Times New Roman, sans-serif; font-size:16px;"><b>' + unicode(i[0]) + '. ' + '<a style="color: #2b2b2b; text-decoration:none;" href="' + unicode(i[1]['url'])+ '"><font color="#2b2b2b">' + unicode(i[1]['title']) + '.</font></a> <br/><br/><font color="#2b2b2b" "text-decoration=none"> ' + unicode(i[1]['source']) + '</font></b><br/><br/></td> </tr> <tr> <td style="font-family:Times New Roman, sans-serif; font-size:16px">' + unicode(i[1]['summary']) + '.</td> </tr> <tr> <td> <table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td style="font-family:Times New Roman, sans-serif;" width="260" valign="top">' + unicode(i[1]['keywords']) + '</td> <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td> <td width="260" valign="top"></td> </tr> </table> </td> </tr> </table><br/><br/><hr align="center" width="80%" style="color:#aec7e8;border-color: #aec7e8;border:2px solid;"></td> </tr>'

# else:
# 	for i in list:
# 		content = content + '<tr border-bottom="1px solid #aec7e8"> <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;"> <table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td style="font-family:Times New Roman, sans-serif; font-size:16px;"><b>' + unicode(i.distance) + '. ' + '<a style="color: #2b2b2b; text-decoration:none;" href="' + unicode(i.url)+ '"><font color="#2b2b2b">' + unicode(i.title) + '.</font></a> <br/><br/><font color="#2b2b2b" "text-decoration=none"> ' + unicode(i.source) + '</font></b><br/><br/></td> </tr> <tr> <td style="font-family:Times New Roman, sans-serif; font-size:16px">' + unicode(i.summary) + '.</td> </tr> <tr> <td> <table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td style="font-family:Times New Roman, sans-serif;" width="260" valign="top">' + unicode(i.keywords) + '</td> <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td> <td width="260" valign="top"></td> </tr> </table> </td> </tr> </table><br/><br/><hr align="center" width="80%" style="color:#aec7e8;border-color: #aec7e8;border:2px solid;"></td> </tr>'


# <!-- Footer -->
content = content + '<tr> <td bgcolor="#aec7e8" style="padding: 30px 30px 30px 30px;"> <table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td style="font-family:Times New Roman, sans-serif;" width="75%"> &copy; Graphite, 2016 <br/></td> <td> <td align="right"> <table border="0" cellpadding="0" cellspacing="0"> <tr> <td></td> <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td> <td></td> </tr> </table> </td> </td> </tr> </table> </td> </tr> </table> </body> </html> '
print 'done'

send_mail('NewsButler general brief - ' + date.today().strftime("%a %d/%m %y"),'Sorry, this service works only for html-compatible mail clients','grphtcontact@gmail.com',[email],connection=None, html_message=content)
