import webpage

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
            if resp.ok:
                locations = self._parse_sitemap(resp.content)
            self.pages_to_crawl.append(site)
            self.pages_to_crawl.extend(locations)
        else:
            self.pages_to_crawl.append(site)

    def _parse_sitemap(self, sitemap):
        '''
        Parse the Sitemap for Locations
        '''
        output = []

        soup = Soup(sitemap, "html.parser")
        urls = soup.findAll('url')

        # get just the locations
        if len(urls) > 0:
            for u in urls:
                loc = u.find('loc').string
                output.append(loc)

        return output

    def _analyze_crawlers(self):
        # robots.txt present
        resp = requests.get(self.domain + "/robots.txt")
        if resp.status_code == 200:
            self.earned(
                u"robots.txt detected.  This helps search engines navigate pages \
                that should be indexed")
        else:
            self.warn(
                u"robots.txt is missing.  \
                A 'robots.txt' file tells search engines whether they \
                can access and therefore crawl parts of your site")

    def warn(self, message):
        self.issues.append(message)

    def earned(self, message):
        self.achieved.append(message)

    def crawl(self):

        # site wide checks
        self._analyze_crawlers()

        # iterate over individual pages to crawl
        for page_url in self.pages_to_crawl:
            resp = requests.get(page_url)

            if resp.status_code == 200:
                html = webpage.Webpage(
                    page_url, resp.content, self.titles, self.descriptions)

                page_report = html.report()
                self.report['pages'].append(page_report)

                # mark the page as crawled
                self.pages_crawled.append(page_url.strip().lower())
            elif resp.status_code == 404:
                self.warn(
                    "Avoid having broken links in your sitemap or website: \
                    {0}".format(page_url))
            else:
                self.warn("Unknown response code detected: \
                {0}: {1}".format(resp.status_code, page_url))

        # aggregate the site wide issues/achievements
        self.report['site'] = {}
        self.report['site']["issues"] = self.issues
        self.report['site']["achieved"] = self.achieved

        return self.report
