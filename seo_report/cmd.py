import website

import sys


def main():
    if len(sys.argv) == 2:
        site_domain = sys.argv[1]

        spider = website.Spider(site_domain)
        spider.crawl()
    elif len(sys.argv) == 3:
        site_domain = sys.argv[1]
        site_map = site_domain + sys.argv[2]

        spider = website.Spider(site_domain, site_map)
        spider.crawl()
    else:
        print ("Usage: seoreport http://www.domain.com [/sitemap.xml]")
        exit

if __name__ == "__main__":
    sys.exit(main())
