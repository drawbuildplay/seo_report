import argparse
import json
import sys

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
        default="/sitemap.xml",
        help='Sitemap.xml file to use'
    )

    return parser


def analyze(domain, sitemap):
    spider = website.Spider(domain, sitemap)
    report = spider.crawl()

    return (json.dumps(report, indent=4, separators=(',', ': ')))


def main():
    parser = create_parser()
    args = parser.parse_args()
    report = analyze(args.domain, args.domain + args.sitemap)

    print (report)

if __name__ == "__main__":
    main()
