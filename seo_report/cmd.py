import argparse
import json

from seo_report import website


def create_parser():
    parser = argparse.ArgumentParser(
        description='Analyze and report on the Search Experience of a website.'
    )

    parser.add_argument(
        '-d', '--domain', type=str, required=True,
        help='Website domain to analyze'
    )

    parser.add_argument(
        '-s', '--sitemap', type=str, required=False,
        help='Sitemap.xml file to use'
    )

    parser.add_argument(
         '-p', '--page', type=str, required=False,
        help='Single Page to analyze'
    )


    return parser


def analyze(domain, sitemap, page):
    spider = website.Spider(domain, sitemap, page)
    report = spider.crawl()

    return (json.dumps(report, indent=4, separators=(',', ': ')))


def main():
    parser = create_parser()
    args = parser.parse_args()
    report = analyze(args.domain, args.sitemap, args.page)

    print(report)

if __name__ == "__main__":
    main()
