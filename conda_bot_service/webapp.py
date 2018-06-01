# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018 Anaconda, Inc.
#
# Licensed under the terms of the MIT License
# (See LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Conda Bot Service Web Application."""

# Standard library imports
import os

# Third party imports
from tornado import gen
from tornado.log import enable_pretty_logging
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web

# Local imports
from gh.event import GithubEvent
from gh.repo import GithubRepo
import cla
import config


# Constants
HERE = os.path.abspath(os.path.dirname(__file__))


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('<h1>Welcome to Conda Service Bot Application!</h1>')


class CLAHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('<h1>Welcome to Conda CLA Service Bot!</h1>')

    @gen.coroutine
    def post(self, headers=None, raw_body=None):
        headers = headers if headers else self.request.headers
        raw_body = raw_body if raw_body else self.request.body
        body = tornado.escape.json_decode(raw_body)
        ge = GithubEvent(headers, raw_body, body)

        if ge.is_ping():
            self.write('pong')
        elif ge.is_pr():
            if ge.is_valid_owner(config.VALID_OWNERS):
                if ge.is_pr_open():
                    # Get Authors & Committers for all commits in PR
                    gr = GithubRepo(config.GH_TOKEN, ge.repo_owner,
                                    ge.repo_name)
                    users = gr.get_pr_users(ge.pr_id)

                    # Check all have signed the CLA
                    cla_doc_url = config.get_cla_url(ge.repo_full_name)
                    check_info = cla.check_users(users, cla_doc_url)
                    gr.set_pr_status(
                        ge.pr_commit_sha,
                        status=check_info.status,
                        description=check_info.description,
                        context=config.GITHUB_BOT_NAME,
                        target_url=config.CLA_INFO_URL,
                    )
            else:
                print('Invalid repository owner')
                self.set_status(404)
                self.write_error(404)
        else:
            print('Unhandled event "{}".'.format(ge.type))
            self.set_status(404)
            self.write_error(404)


def create_webapp():
    enable_pretty_logging()
    application = tornado.web.Application(
        [
            (r"/", IndexHandler),
            (r"/cla/hook", CLAHandler),
        ],
        debug=True,
    )
    return application


def main():
    application = create_webapp()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    port = config.PORT
    n_processes = config.WEB_CONCURRENCY

    if n_processes != 1:
        # http://www.tornadoweb.org/en/stable/guide/running.html#processes-and-ports
        http_server.bind(port)
        http_server.start(n_processes)
    else:
        http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
