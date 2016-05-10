import ddt
import mock
import testtools
import uuid

from seo_report import website


@ddt.ddt
class WebsiteTests(testtools.TestCase):

    def setUp(self):
        super(WebsiteTests, self).setUp()

        self.site_url = "http://www.mock{0}.com".format(uuid.uuid4())

    def test_init_url(self):
        wp = website.Spider(self.site_url, None)

        self.assertEqual(len(wp.pages_to_crawl), 1)
        self.assertEqual(wp.pages_to_crawl[0], self.site_url)

    @ddt.file_data("data_sitemap.json")
    @mock.patch('website.requests.get')
    def test_init_sitemap(self, content, mock_requests):
        sitemap_url = "/sitemap.xml"

        mock_requests.return_value.status_code = 200
        mock_requests.return_value.content = content

        wp = website.Spider(self.site_url, self.site_url + sitemap_url)

        self.assertTrue(self.site_url in wp.pages_to_crawl)

    @ddt.file_data("data_sitemap.json")
    def test_parse_sitemap(self, sitemap_content):
        wp = website.Spider(self.site_url, None)

        locations = wp._parse_sitemap(sitemap_content)

        self.assertEqual(len(locations), 2)

    @ddt.file_data("data_webpage.json")
    @mock.patch('website.requests.get')
    def test_crawl(self, data, mock_requests):
        wp = website.Spider(self.site_url, None)
        wp._analyze_crawlers = mock.MagicMock(name="_analyze_crawlers")

        # set up the mocked responses
        resp_code, content = data.split("|")

        mock_requests.return_value.status_code = int(resp_code)
        mock_requests.return_value.content = content
        report = wp.crawl()

        if int(resp_code) == 404:
            self.assertTrue(any(issue.startswith('Avoid having broken links')
                                for issue in wp.issues))
        else:
            self.assertEqual(len(wp.issues), 0)

    @ddt.data("200", "404")
    @mock.patch('website.requests.get')
    def test_analyze_crawlers(self, resp_code, mock_requests):
        mock_requests.return_value.status_code = int(resp_code)

        wp = website.Spider(self.site_url, None)
        wp._analyze_crawlers()

        if int(resp_code) == 200:
            self.assertTrue(any(earned.startswith('robots.txt detected.')
                                for earned in wp.achieved))
        else:
            self.assertTrue(any(issue.startswith('robots.txt is missing.')
                                for issue in wp.issues))
