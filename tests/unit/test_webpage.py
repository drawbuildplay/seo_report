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

    @ddt.file_data('data_html_positive.json')
    def test_analyze_positive(self, data):
        html = data[0]
        expected_achievement = data[1]

        self.wp = webpage.Webpage(
            "url.com", html, self.titles, self.descriptions)
        self.wp.report()

        # title should have achieved the following
        self.assertTrue(any(earned.startswith(expected_achievement)
                            for earned in self.wp.achieved),
                        "{0} not found".format(expected_achievement))

    @ddt.file_data('data_html_negative.json')
    def test_analyze_negative(self, data):
        html = data[0]
        expected_error = data[1]

        self.wp = webpage.Webpage(
            "url.com", html, self.titles, self.descriptions)

        self.wp.report()
        self.assertTrue(any(issue.startswith(expected_error)
                            for issue in self.wp.issues),
                        "{0} not found in issues".format(expected_error))

    def test_analyze_url(self):
        pass

    def test_analyze_duplicate_titles(self):
        pass

    def test_analyze_duplicate_descriptions(self):
        pass
