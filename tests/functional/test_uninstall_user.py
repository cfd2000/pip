"""
tests specific to uninstalling --user installs
"""
from os.path import isdir, isfile, normcase

import pytest

from tests.functional.test_install_user import _patch_dist_in_site_packages
from tests.lib import assert_all_changes, pyversion


class Tests_UninstallUserSite:

    @pytest.mark.network
    def test_uninstall_from_usersite(self, script):
        """
        Test uninstall from usersite
        """
        result1 = script.pip('install', '--user', 'INITools==0.3')
        result2 = script.pip('uninstall', '-y', 'INITools')
        assert_all_changes(result1, result2, [script.venv / 'build', 'cache'])

    def test_uninstall_from_usersite_with_dist_in_global_site(
            self, virtualenv, script):
        """
        Test uninstall from usersite (with same dist in global site)
        """
        _patch_dist_in_site_packages(virtualenv)

        script.pip_install_local('pip-test-package==0.1', '--no-binary=:all:')

        result2 = script.pip_install_local(
            '--user', 'pip-test-package==0.1.1', '--no-binary=:all:')
        result3 = script.pip('uninstall', '-vy', 'pip-test-package')

        # uninstall console is mentioning user scripts, but not global scripts
        assert normcase(script.user_bin_path) in result3.stdout, str(result3)
        assert normcase(script.bin_path) not in result3.stdout, str(result3)

        # uninstall worked
        assert_all_changes(result2, result3, [script.venv / 'build', 'cache'])

        # site still has 0.2 (can't look in result1; have to check)
        egg_info_folder = (
            script.base_path / script.site_packages /
            'pip_test_package-0.1-py%s.egg-info' % pyversion
        )
        assert isdir(egg_info_folder)

    def test_uninstall_editable_from_usersite(self, script, data):
        """
        Test uninstall editable local user install
        """
        script.user_site_path.makedirs()

        # install
        to_install = data.packages.joinpath("FSPkg")
        result1 = script.pip(
            'install', '--user', '-e', to_install, expect_error=False,
        )
        egg_link = script.user_site / 'FSPkg.egg-link'
        assert egg_link in result1.files_created, str(result1.stdout)

        # uninstall
        result2 = script.pip('uninstall', '-y', 'FSPkg')
        assert not isfile(script.base_path / egg_link)

        assert_all_changes(
            result1,
            result2,
            [
                script.venv / 'build',
                'cache',
                script.user_site / 'easy-install.pth',
            ]
        )
