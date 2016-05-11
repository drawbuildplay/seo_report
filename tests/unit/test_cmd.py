import ddt
import json
import jsonschema
import mock
import sys
import testtools
import uuid

from seo_report import cmd


@ddt.ddt
class CmdTests(testtools.TestCase):

    def setUp(self):
        super(CmdTests, self).setUp()
        pass

    @ddt.data(
        "--domain http://www.mock{0}.com",
        "--domain http://www.mock{0}.com --sitemap /sitemap.xml",
        "--domain http://www.mock{0}.com --sitemap /private_sitemap.xml")
    def test_create_parser(self, data):
        args = data.format(uuid.uuid4())
        argv = args.split()

        domain = argv[1]
        sitemap = argv[3] if len(argv) > 3 else "/sitemap.xml"

        parser = cmd.create_parser()
        args = parser.parse_args(argv)

        self.assertEqual(args.domain, domain)
        self.assertEqual(args.sitemap, sitemap)

    @ddt.data(
        "",
        "--mysite http://www.mock{0}.com",
        "--domain http://www.mock{0}.com --mymap /sitemap.xml")
    def test_create_parser_invalid_args(self, data):
        args = data.format(uuid.uuid4())
        argv = args.split()
        parser = cmd.create_parser()

        self.assertRaises(SystemExit, parser.parse_args, argv)

    @mock.patch('seo_report.website.requests.get')
    def test_analyze(self, mock_requests):

        domain = "http://www.mock{0}.com".format(uuid.uuid4())
        sitemap = domain + "/sitemap.xml"

        report = json.loads(cmd.analyze(domain, sitemap))

        jsonschema.validate(report, self.report_schema)
        self.assertTrue(jsonschema.Draft3Validator(
            self.report_schema).is_valid(report))

    @ddt.data("--domain http://www.mock{0}.com")
    @mock.patch('seo_report.website.requests.get')
    def test_main(self, data, mock_requests):

        sys.argv[1:] = data.format(uuid.uuid4()).split()
        cmd.main()

    @ddt.data("--invalid http://www.mock{0}.com", "")
    @mock.patch('seo_report.website.requests.get')
    def test_main_negative(self, data, mock_requests):

        sys.argv[1:] = data.format(uuid.uuid4()).split()
        self.assertRaises(SystemExit, cmd.main)

    report_schema = {
        'type': 'object',
        'properties': {
            "pages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                        },
                        "keywords": {
                            "type": "string",
                        },
                        "title": {
                            "type": "string",
                        },
                        "description": {
                            "type": "string",
                        },
                        "issues": {
                            "type": "array",
                        },
                        "achieved": {
                            "type": "array",
                        }
                    },
                    "additionalProperties": False
                }
            },
            "site": {
                "type": "object",
                "items": {
                    "type": "object",
                    "properties": {
                        "issues": {
                            "type": "array",
                        },
                        "achieved": {
                            "type": "array",
                        }
                    }
                }
            }
        },
        "additionalProperties": False
    }
