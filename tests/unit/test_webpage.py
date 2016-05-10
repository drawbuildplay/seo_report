import bs4
import ddt
import testtools

from seo_report import webpage


@ddt.ddt
class WebpageTests(testtools.TestCase):

    def setUp(self):
        super(WebpageTests, self).setUp()

        self.titles = {}
        self.descriptions = {}

    def soup_file(self, html):
        soup = bs4.BeautifulSoup(html, "html.parser")
        return soup

    @ddt.file_data('data_title_positive.json')
    def test_analyze_title_positive(self, html):
        self.wp = webpage.Webpage(
            "url.com", html, self.titles, self.descriptions)
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

    @ddt.file_data('data_title_negative.json')
    def test_analyze_title_negative(self, html):
        self.wp = webpage.Webpage(
            "url.com", html, self.titles, self.descriptions)
        doc = self.soup_file(html)
        self.wp._analyze_title(doc)

        # one thing should be wrong with this title
        self.assertEqual(len(self.wp.issues), 1)
