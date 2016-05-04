import website

import sys


if __name__ == '__main__':

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
        print ("Usage: python report_seo www.domain.com [/sitemap.xml]")
        exit
        
