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
            "https://www.drawbuildplay.com",
            html,
            self.titles,
            self.descriptions)

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
            "https://www.drawbuildplay.com",
            html,
            self.titles,
            self.descriptions)

        self.wp.report()
        self.assertTrue(any(issue.startswith(expected_error)
                            for issue in self.wp.issues),
                        "{0} not found in issues".format(expected_error))

    @ddt.file_data('data_html_negative_url.json')
    def test_analyze_negative_url(self, data):
        url = data[0]
        expected_error = data[1]
        html = ""

        self.wp = webpage.Webpage(
            url, html, self.titles, self.descriptions)

        self.wp.report()
        self.assertTrue(any(issue.startswith(expected_error)
                            for issue in self.wp.issues),
                        "{0} not found in issues".format(expected_error))

    def test_analyze_duplicate_titles(self):
        pass

    def test_analyze_duplicate_descriptions(self):
        pass

    @ddt.file_data('data_visible_tags.json')
    def test_visible_tags(self, data):
        html = ""
        self.wp = webpage.Webpage(
            "https://www.drawbuildplay.com",
            html,
            self.titles,
            self.descriptions)

        soup = self.soup_file(data[0])
        elements = soup.findAll(text=True)
        for tag in elements:
            result = self.wp.visible_tags(tag)
            self.assertEqual(result, data[1])
