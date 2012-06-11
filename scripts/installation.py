# -*- coding: utf-8 -*-
"""
    installation

    A script to install the modules

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import os
import logging
from subprocess import call

logging.basicConfig(level=logging.INFO)

GITHUB_MODULES = (
    "git@github.com:openlabs/nereid.git",
    "git@github.com:openlabs/nereid-catalog.git",
    "git@github.com:openlabs/nereid-cart-b2c.git",
    "git@github.com:openlabs/nereid-checkout.git",
    "git@github.com:openlabs/nereid-payment.git",
    "git@github.com:openlabs/nereid-auth-facebook.git",
)


def install():
    for module in GITHUB_MODULES:
        folder = module.rsplit('/')[-1].split('.')[0]

        logging.info("working on %s" % folder)

        if not os.path.exists("src/%s" % folder):
            logging.info("cloning module as folder does not exist")
            call(["git", "clone", module, "src/%s" % folder])
        else:
            logging.info("updating the module")
            call(["cd", "src/%s" % folder, "&&", "git", "pull"])



if __name__ == '__main__':
    install()
