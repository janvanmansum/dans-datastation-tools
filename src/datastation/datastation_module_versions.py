import os

import rich

from datastation.common.module_info import get_rpm_versions


def main():
    rpm_modules = get_rpm_versions('dans.knaw.nl-')
    rich.print(rpm_modules)


if __name__ == '__main__':
    main()
