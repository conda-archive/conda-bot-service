# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018 Anaconda, Inc.
# Copyright (c) 2016, conda-forge
#
# Licensed under the terms of the MIT License
# (See LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Conda CLA utils."""

# Third party imports
import requests

# Local imports
from gh.repo import GithubRepo


# Constants
FAILURE = GithubRepo.FAILURE
SUCCESS = GithubRepo.SUCESS


class CheckInfo(object):

    def __init__(self, status, description):
        self.status = status
        self.description = description


def _get_cla_raw_data(cla_document_url):
    """Parse the `cla_document_url` content and return a list of `Signer`."""
    data = ''
    error = None
    try:
        r = requests.get(cla_document_url)
    except Exception as error:
        pass

    if error is None or r.status_code in [200]:
        data = r.text

    return data


def _process_cla_data(data):
    """Parse the `cla_document_url` content and return a list of `Signer`."""
    signers = []
    if data:
        lines = data.strip().split('\n')
        uncommented_lines = [l for l in lines if not l.strip().startswith('#')]
        for line in uncommented_lines:
            parts = [part.strip() for part in line.split('|')]
            signers.append(parts[0])

    return signers


def _format_item_list(items, pad="'", sep=', ', end_sep=' and '):
    """
    Format a list of items.

    Result is in the form [pad + item + pad + sep + ... + end_sep + last_item]
    """
    result = ''
    items = [pad + item + pad for item in items]
    if items:
        if len(items) != 1:
            result = sep.join(items[:-1]) + end_sep + items[-1]
        else:
            result = items[0]
    return result


def _create_check_info(check, signers, non_signers):
    """Generate an information object."""
    status = SUCCESS if check else FAILURE

    if len(signers) == 0 and len(non_signers) == 0:
        base_description = ''
        text = 'No users have been checked for CLA compliance.{0}'
        value = ''
    else:
        total = len(signers) + len(non_signers)
        base_description = '{0}/{1} CLA checks passed. '.format(len(signers),
                                                                total)
        if check:
            value = _format_item_list(signers)
            text = ''
        else:
            value = _format_item_list(non_signers)
            if len(non_signers) == 1:
                text = 'User {} has not signed the CLA document.'
            else:
                text = 'Users {} have not signed the CLA document.'

    description = base_description + text.format(value)

    return CheckInfo(status, description)


def check_users(github_users, cla_document_url, default_check=True):
    """
    Check if `github_user` is found in the given `cla_document_url`.

    In case te cla_document is empty or does not exist the return value is
    the one set by default_check.
    """
    data = _get_cla_raw_data(cla_document_url)
    signers = _process_cla_data(data)
    current_non_signers = []
    current_signers = []

    if signers:
        for user in github_users:
            if user in signers:
                current_signers.append(user)
            else:
                current_non_signers.append(user)

        check = not bool(current_non_signers)
    else:
        check = default_check

    info = _create_check_info(check, current_signers, current_non_signers)

    return info
