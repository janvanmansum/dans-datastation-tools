from io import StringIO
from unittest.mock import patch

from datastation.common.result_writer import JsonResultWriter
from datastation.dans_bag.dans_bag_validator import DansBagValidator


class TestDansBagValidator:

    def test_post_not_called_when_dry_run(self):
        with patch('requests.post') as mock_post:
            config = {'service_base_url': 'http://service-base-url'}
            validator = DansBagValidator(config, dry_run=True)
            validator.validate_dans_bag('some/path', 'SIP', None)
            mock_post.assert_not_called()

    def test_post_called_when_not_dry_run(self):
        with patch('requests.post') as mock_post:
            # expected result is not important here
            mock_post.return_value.text = '{}'
            config = {'service_base_url': 'http://service-base-url'}
            validator = DansBagValidator(config, dry_run=False)
            validator.validate_dans_bag('some/path', 'SIP', JsonResultWriter(StringIO()))
            mock_post.assert_called_once()

    def test_post_called_with_expected_url(self):
        with patch('requests.post') as mock_post:
            # expected result is not important here
            mock_post.return_value.text = '{}'
            config = {'service_base_url': 'http://service-base-url'}
            validator = DansBagValidator(config, dry_run=False)
            validator.validate_dans_bag('some/path', 'SIP', JsonResultWriter(StringIO()))
            mock_post.assert_called_once_with('http://service-base-url/validate', data=mock_post.call_args[1]['data'],
                                              headers=mock_post.call_args[1]['headers'])
