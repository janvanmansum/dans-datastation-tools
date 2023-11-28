import os
from re import match


def rpm_qa():
    return os.popen('rpm -qa')


evr_pattern = r'(?P<name>.*?)-(?P<version>\d+\.\d+\.\d+)-(?P<release>\d+)'


def get_rpm_versions(prefix):
    """Get the versions of the RPMs installed on the system."""
    rpm_versions = {}
    for line in rpm_qa():
        if line.startswith(prefix):
            evr = match(evr_pattern, line)
            version = evr.group('version')
            module = evr.group('name')
            rpm_versions[module] = version

    return rpm_versions


def get_dataverse_version(dataverse_application_path):
    with open(os.path.join(dataverse_application_path, 'WEB-INF', 'classes', 'META-INF',
                           'microprofile-config.properties'), 'r') as f:
        for line in f:
            if 'dataverse.version' in line:
                return line.split('"')[1]


def get_dataverse_build_number(dataverse_application_path):
    with open(os.path.join(dataverse_application_path, 'WEB-INF', 'classes', 'BuildNumber.properties'), 'r') as f:
        for line in f:
            if 'build.number' in line:
                return line.split('"')[1]


def get_payara_version(payara_application_path):
    with open(os.path.join(payara_application_path, 'glassfish', 'modules', 'org', 'glassfish', 'main',
                           'glassfish-api.jar'), 'r') as f:
        for line in f:
            if 'Implementation-Version' in line:
                return line.split(' ')[1].strip()
