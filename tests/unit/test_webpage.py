import bs4
import ddt
import mock
import testtools
import requests

from seo_report import webpage

@ddt.ddt
class WebpageTests(testtools.TestCase):

    def setUp(self):
        super(WebpageTests, self).setUp()
        
        self.titles = {}
        self.descriptions = {}
        self.wp = webpage.Webpage("url", self.titles, self.descriptions)
        pass
        
    def soup_file(self, html):
        soup = bs4.BeautifulSoup(html, "html.parser")
        return soup
        
    @ddt.file_data('data_title_positive.html')
    def test_analyze_title_positive(self, html):
        doc = self.soup_file(html)
        self.wp._analyze_title(doc)
        
        # nothing should be wrong with this title
        self.assertEqual(len(self.wp.issues), 0)
        
        # title should have achieved the following
        self.assertTrue("Title is a great length" in self.wp.achieved)
        self.assertTrue("Title is informative" in self.wp.achieved)
        self.assertTrue("This page has a unique title tag" in self.wp.achieved)
        self.assertEqual(len(self.wp.achieved), 3)
        
        # title should be added to the list of all titles
        self.assertTrue(self.wp.title in self.titles)
        
    @ddt.file_data('data_title_negative.html')
    def test_analyze_title_negative(self, html):
        doc = self.soup_file(html)
        self.wp._analyze_title(doc)
        
        # nothing should be wrong with this title
        self.assertEqual(len(self.wp.issues), 0)
        
        # title should have achieved the following
        
        # title should be added to the list of all titles
        
        
        
        