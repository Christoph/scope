import pytest


@pytest.fixture
def load():
    from scope.methods.dataprovider import url_extractor

    ex = url_extractor.Extractor()

    return ex


def test_urls(load):
    assert len(load.get_urls_from_string(urls_good)) == 5

def test_blacklists(load):
    assert len(load.get_urls_from_string(urls_bad)) == 0




urls_good = (
    "http://hyperallergic.com/343745/"
    "the-passionate-art-of-lgbtq-prisoners-in-the-us/"
    " "
    "http://www.androidheadlines.com/2016/12/"
    "verizon-carry-blackberry-mercury-bbb100-us.html"
    " "
    "http://www.usnews.com/news/business/articles/2016-12-27/"
    "troubled-italian-bank-says-capital-hole-bigger-than-expected"
    " "
    "http://www.androidheadlines.com/2016/12/"
    "verizon-carry-blackberry-mercury-bbb100-us.html"
    " "
    "http://www.usnews.com/news/stem-solutions/articles/"
    "2016-11-28/wi-fi-microscopes-help-corpus-christi-students-with-science"
    " "
    )

urls_bad = (
    "https://twitter.com/SteveMartinToGo/status/813826846722760705"
    " "
)
