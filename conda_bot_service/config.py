# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018 Anaconda, Inc.
#
# Licensed under the terms of the MIT License
# (See LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Conda CLA web services."""

# Standard library imports
import os

# Webapp
# ------
# https://devcenter.heroku.com/articles/optimizing-dyno-usage#python
PORT = int(os.environ.get("PORT", 5000))
WEB_CONCURRENCY = int(os.environ.get("WEB_CONCURRENCY", 1))

# Github vars. Environment variables on web service infrastructure
# ----------------------------------------------------------------
GH_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
GH_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET')

# Bot configuration
# -----------------
VALID_OWNERS = ('conda', 'conda-build', 'goanpeca')
GITHUB_BOT = 'conda-bot'
GITHUB_BOT_NAME = 'Conda Contributor License Agreement'

# CLA document urls
# -----------------
CLA_DOCUMENT_URLS = {
    'conda/conda':
        "https://raw.githubusercontent.com/conda/conda/master/.cla-signers",
    # For testing
    'goanpeca/conda-bot-service':
        "https://raw.githubusercontent.com/goanpeca/conda-bot-service/"
        "master/.cla-signers",
}
CLA_INFO_URL = 'https://conda.io/docs/contributing.html#conda-contributor-license-agreement'


def get_cla_url(repo_full_name):
    return CLA_DOCUMENT_URLS.get(repo_full_name)
