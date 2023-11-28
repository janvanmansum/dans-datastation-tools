from rich.console import Console
from rich.table import Table

from datastation.common.config import init
from datastation.common.version_info import get_rpm_versions, get_dataverse_version


def main():
    config = init()
    components = get_rpm_versions(config['version_info']['dans_rpm_module_prefix'])
    dataverse_version = get_dataverse_version(config['version_info']['dataverse_application_path'])
    components['dataverse'] = dataverse_version
    payara_version = get_dataverse_version(config['version_info']['payara_install_path'])
    components['payara'] = payara_version
    table = Table(title="Data Station Component Versions")
    table.add_column("Component")
    table.add_column("Version")
    for component in components:
        table.add_row(component, components[component])
    console = Console()
    console.print(table)


if __name__ == '__main__':
    main()
