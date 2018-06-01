# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018 Anaconda, Inc.
# Copyright (c) 2016, conda-forge
#
# Licensed under the terms of the MIT License
# (See LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Conda CLA web services."""

# Third party imports
import github


class GithubRepo:
    """"""

    # Github PR Status
    SUCESS = 'success'
    FAILURE = 'failure'

    def __init__(self, token, repo_owner, repo_name):
        """"""
        self._gh = github.Github(token)
        self._user = self._gh.get_user(repo_owner)
        self._repo = self._user.get_repo(repo_name)

    def get_pr_users(self, pr_id):
        """Return all the users (authors and committers) for a giver pr."""
        issue = self._repo.get_pull(pr_id)
        commits = issue.get_commits()
        authors = set()
        committers = set()
        for commit in commits:
            authors.add(commit.author.login.lower())
            committers.add(commit.committer.login.lower())

        # Remove the `web-flow` github user in case a PR was editted in the
        # github web interface
        web_flow_committer = 'web-flow'
        if web_flow_committer in committers:
            committers.remove(web_flow_committer)

        return authors.union(committers)

    def comment_pr(
            self,
            pr_id,
            message,
            force=False,
            ):
        """Post message on pull request `pr_id` on comments thread."""
        issue = self._repo.get_issue(pr_id)

        if force:
            return issue.create_comment(message)

        comments = list(issue.get_comments())
        comment_owners = [comment.user.login for comment in comments]

        my_last_comment = None
        my_login = self._gh.get_user().login
        if my_login in comment_owners:
            my_last_comment = [comment for comment in comments
                               if comment.user.login == my_login][-1]

        # Only comment if we haven't before, or if the message is different
        if my_last_comment is None or my_last_comment.body != message:
            my_last_comment = issue.create_comment(message)

        return my_last_comment

    def set_pr_status(
            self,
            commit_sha,
            status=FAILURE,
            description=None,
            context=None,
            target_url=None,
            ):
        """Set the status of a given commit on a pull request."""
        commit = self._repo.get_commit(commit_sha)
        result = commit.create_status(
            status,
            description=description,
            context=context,
            target_url=target_url,
        )

        return result
