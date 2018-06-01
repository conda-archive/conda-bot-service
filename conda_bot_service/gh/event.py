# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018 Anaconda, Inc.
#
# Licensed under the terms of the MIT License
# (See LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Github webhook."""


class GithubEvent:

    def __init__(self, headers, raw_body, body):
        self._headers = headers
        self._raw_body = raw_body
        self._body = body
        self.repo_full_name = body['repository']['full_name']
        self.repo_owner, self.repo_name = self.repo_full_name.split('/')
        self.type = headers.get('X-GitHub-Event', None)
        self._is_pr = self.type == 'pull_request'
        self._is_ping = self.type == 'ping'

    @property
    def user(self):
        if self._is_pr:
            return self._body['pull_request']['user']['login']

    @property
    def pr_commit_sha(self):
        if self._is_pr:
            return self._body['pull_request']['head']['sha']

    @property
    def pr_id(self):
        if self._is_pr:
            return int(self._body['pull_request']['number'])

    def is_pr(self):
        return self._is_pr

    def is_ping(self):
        return self._is_ping

    def is_pr_open(self):
        state = False
        if self._is_pr:
            state = self._body['pull_request']['state'] == 'open'

        return state

    def is_valid_owner(self, valid_owners):
        valid_owners = [owner.lower() for owner in valid_owners]
        return self.repo_owner.lower() in valid_owners
