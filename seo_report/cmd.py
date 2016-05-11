import json
import sys

from seo_report import website


def main():
    if len(sys.argv) == 2:
        site_domain = sys.argv[1]

        spider = website.Spider(site_domain)
        report = spider.crawl()

        print(json.dumps(report, indent=4, separators=(',', ': ')))

    elif len(sys.argv) == 3:
        site_domain = sys.argv[1]
        site_map = site_domain + sys.argv[2]

        spider = website.Spider(site_domain, site_map)
        report = spider.crawl()

        print(json.dumps(report, indent=4, separators=(',', ': ')))

    else:
        print("Usage: seoreport http://www.domain.com [/sitemap.xml]")
        exit

if __name__ == "__main__":
    sys.exit(main())
