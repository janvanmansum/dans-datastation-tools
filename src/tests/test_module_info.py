from unittest.mock import patch

from datastation.common.module_info import get_rpm_versions


def test_only_modules_with_matching_prefix_found():
    with patch('datastation.common.module_info.rpm_qa') as mock_qa:
        mock_qa.return_value = ['dans.knaw.nl-dd-vault-metadata-2.2.0-1.noarch',
                                'dans.knaw.nl-dans-schema-0.10.0-1.noarch',
                                'python3-rpm-generators-5-8.el8.noarch',
                                'dans.knaw.nl-dd-verify-dataset-0.10.0-1.noarch',
                                ]
        versions = get_rpm_versions('dans.knaw.nl-')
        assert versions == {
            'dans.knaw.nl-dd-vault-metadata': '2.2.0',
            'dans.knaw.nl-dans-schema': '0.10.0',
            'dans.knaw.nl-dd-verify-dataset': '0.10.0'
        }


def test_no_modules_found():
    with patch('datastation.common.module_info.rpm_qa') as mock_qa:
        mock_qa.return_value = ['python3-rpm-generators-5-8.el8.noarch']
        versions = get_rpm_versions('dans.knaw.nl-')
        assert versions == {}
