import ddt
import json
import jsonschema
import mock
import testtools
import uuid

from seo_report import cmd


@ddt.ddt
class CmdTests(testtools.TestCase):

    def setUp(self):
        super(CmdTests, self).setUp()
        pass

    def test_create_parser(self):
        pass

    @mock.patch('seo_report.website.requests.get')
    def test_analyze(self, mock_requests):

        domain = "http://www.mock{0}.com".format(uuid.uuid4())
        sitemap = domain + "/sitemap.xml"

        report = json.loads(cmd.analyze(domain, sitemap))

        jsonschema.validate(report, self.report_schema)
        self.assertTrue(jsonschema.Draft3Validator(self.report_schema).is_valid(report))

    def test_main(self):
        pass

    
    report_schema = {
        'type': 'object',
        'properties': {
            "pages": {
                "type": "array"
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
