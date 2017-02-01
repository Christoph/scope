EXCLUDE = set(('',
               'FT.com / Registration / Sign-up',
               'Error', '404 Page not found',
               'Page no longer available',
               'File or directory not found',
               'Page not found',
               'Content not found',
               'Seite nicht gefunden',
               '404 :: lr-online',
               'kinja.com',
               'inFranken.de'))

URL_EXCLUDE = set(('kinja.com', 'inFranken.de'))

TEXT_BLACKLIST = [
    "If you are not redirected automatically, please click the Unsubscribe button below.",
    "Add a location to your TweetsWhen you tweet with a location, Twitter stores that location.",
    "diesen Tweet zu deiner Website hinzu, indem Du den untenstehenden Code"
]

SUBSCRIBED_URLS = ["launch.us", "launch.co", "index.co", "azhar",
                   "getrevue.co", "morningreader.com", "producthunt.com",
                   "betalist", "crunchable", "mailchimp.com", "facebook.com",
                   "twitter.com", "launchticker", "play.google.com",
                   "www.technologyreview.com/newsletters",
                   "launchevents.typeform.com", "ev.inside.com",
                   "itunes.apple.com",
                   "https://www.technologyreview.com/?utm_source",
                   "typeform", "producthunt.us3.list-manage.com",
                   "getfeedback", "youtube.com", "forms/", "smashingmagazine",
                   "wikipedia.org"]

URL_PATH_BLACKLIST = ["/unsupported-browser"]

TITLE_BLACKLIST = ["Bei Twitter anmelden",
                   "Inside is creating The Inside Daily Brief",
                   "diesen Tweet zu Deiner Webseite hinzu, indem Du den untenstehenden Code",
                   "Subscribe to read",
                   "Job Application Form",
                   "This Week In Startups",
                   "Smashing Email Newsletter"]

URL_HOSTNAME_BLACKLIST = ["www.facebook.com",
                          "www.producthunt.com",
                          "www.technologyreview.com",
                          "www.morningreader.com",
                          "www.mailchimp.com",
                          "www.twitter.com",
                          "twitter.com",
                          "facebook.com",
                          "play.google.com",
                          "newsletter.inside.com",
                          "www.technologyreview.com/newsletters",
                          "www.typeform.com",
                          "ev.inside.com",
                          "itunes.apple.com",
                          "www.youtube.com",
                          "www.wikipedia.org",
                          "betalist.com",
                          "searchsystem.co",
                          "www.smashingmagazine.com"]
