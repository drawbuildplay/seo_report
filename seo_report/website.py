from seo_report import webpage
from seo_report.warnings import WARNINGS
from seo_report.warnings import BADGES

from bs4 import BeautifulSoup as Soup
import requests
from six.moves.urllib import parse


class Spider(object):
    report = {"pages": []}

    def __init__(self, site, sitemap=None):
        parsed_url = parse.urlparse(site)

        self.domain = "{0}://{1}".format(parsed_url.scheme, parsed_url.netloc)
        self.pages_crawled = []
        self.pages_to_crawl = []
        self.titles = {}
        self.descriptions = {}
        self.issues = []
        self.achieved = []

        # look for the sitemap on this page
        if sitemap is not None:
            # add all locations in the sitemap to the pages_to_crawl table
            locations = []
            resp = requests.get(sitemap)
            if resp.status_code == requests.codes.ok:
                locations = self._parse_sitemap(resp.content)

            self.pages_to_crawl.append(site)
            self.pages_to_crawl.extend(locations)
        else:
            self.pages_to_crawl.append(site)

    def _parse_sitemap(self, sitemap):
        '''
        Parse the Sitemap for Locations
        '''
        locations = []

        soup = Soup(sitemap, "html.parser")
        urls = soup.findAll('url')

        # get just the locations
        if len(urls) > 0:
            for u in urls:
                loc = u.find('loc').string
                locations.append(loc)

        return locations

    def _analyze_crawlers(self):
        # robots.txt present
        resp = requests.get(self.domain + "/robots.txt")
        if resp.status_code == 200:
            self.earned(BADGES["ROBOTS.TXT"])
        else:
            self.warn(WARNINGS["ROBOTS.TXT"])

    def _analyze_mobile(self):
        pass

    def _analyze_analytics(self):
        # Use Google Analytics or Omniture etc
        pass

    def warn(self, message, value=None):
        self.issues.append(
            {
                "warning": message,
                "value": value
            }
        )

    def earned(self, message, value=None):
        self.achieved.append(
            {
                "achievement": message,
                "value": value
            }
        )

    def crawl(self):
        # site wide checks
        self._analyze_crawlers()
        self._analyze_mobile()
        self._analyze_analytics()

        # iterate over individual pages to crawl
        for page_url in self.pages_to_crawl:
            print("Crawled {0} Pages of {1}".format(
                len(self.pages_crawled), len(self.pages_to_crawl)))
            resp = requests.get(page_url)

            if resp.status_code == requests.codes.ok:
                html = webpage.Webpage(
                    page_url, resp.content, self.titles, self.descriptions)

                page_report = html.report()
                self.report['pages'].append(page_report)

                # mark the page as crawled
                self.pages_crawled.append(page_url.strip().lower())
            elif resp.status_code == requests.codes.not_found:
                self.warn(WARNINGS["BROKEN_LINK"], page_url)
            else:
                self.warn(WARNINGS["SERVER_ERROR"],
                          "HTTP{0} received for {1}".format(
                              resp.status_code, page_url))

        # aggregate the site wide issues/achievements
        self.report['site'] = {}
        self.report['site']["issues"] = self.issues
        self.report['site']["achieved"] = self.achieved

        return self.report
