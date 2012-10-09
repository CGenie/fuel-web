# -*- coding: utf-8 -*-

import os
import re
import json
import logging
from random import randint
from unittest.case import TestCase

import mock
from paste.fixture import TestApp
from sqlalchemy.orm.events import orm

from api.models import engine, Node, Release, Cluster
from api.urls import urls
from manage import app
from db import dropdb, syncdb, flush
from fixtures.fixman import upload_fixture


class BaseHandlers(TestCase):

    fixture_dir = "fixtures"
    fixtures = []

    def __init__(self, *args, **kwargs):
        super(BaseHandlers, self).__init__(*args, **kwargs)
        self.mock = mock

    @classmethod
    def setUpClass(cls):
        dropdb()
        syncdb()

    def setUp(self):
        self.app = TestApp(app.wsgifunc())
        self.db = orm.scoped_session(orm.sessionmaker(bind=engine))()
        self.default_headers = {
            "Content-Type": "application/json"
        }
        flush()
        for fxtr in self.fixtures:
            fxtr_path = os.path.join(
                self.fixture_dir,
                "%s.json" % fxtr
            )
            if not os.path.exists(fxtr_path):
                logging.warning(
                    "Fixture file not found: %s",
                    fxtr_path
                )
                break
            else:
                logging.info(
                    "Uploading fixture from file: %s",
                    fxtr_path
                )
                with open(fxtr_path, "r") as fixture:
                    upload_fixture(fixture)

    def default_metadata(self):
        metadata = {'block_device':
                    ['sda', {'size': '16777216'},
                     'ram0', {'size': '131072'}],
                    'interfaces': 'd',
                    'cpu': {'real': 2, 'total': 4},
                    'memory': {'total': '1594988kB'}}
        return metadata

    def _generate_random_mac(self):
        mac = [randint(0x00, 0x7f) for _ in xrange(6)]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def create_release_api(self):
        resp = self.app.post(
            '/api/releases',
            params=json.dumps({
                'name': 'Another test release',
                'version': '1.0'
            }),
            headers=self.default_headers
        )
        self.assertEquals(resp.status, 201)
        return json.loads(resp.body)

    def get_default_networks_metadata(self):
        return [
            {"name": "floating", "access": "public"},
            {"name": "fixed", "access": "private10"},
            {"name": "storage", "access": "private192"},
            {"name": "management", "access": "private172"},
            {"name": "other_172", "access": "private172"}
        ]

    def get_default_attributes_metadata(self):
        return {
            "editable": {
                "keystone": {
                    "admin_tenant": "admin"
                }
            },
            "generated": {
                "mysql": {
                    "root_password": "",
                    "predefined": "i am value",
                    "db": {
                        "generated_db": ""
                    }
                },
                "keystone": {
                    "token": ""
                }
            }
        }

    def create_default_node(self, cluster_id=None):
        node = Node()
        node.mac = self._generate_random_mac()
        node.cluster_id = cluster_id
        node.meta = self.default_metadata()
        self.db.add(node)
        self.db.commit()
        return node

    def create_default_release(self):
        release = Release()
        release.version = randint(0, 100000000)
        release.name = u"release_name_" + str(release.version)
        release.description = u"release_desc" + str(release.version)
        release.networks_metadata = self.get_default_networks_metadata()
        release.attributes_metadata = self.get_default_attributes_metadata()
        self.db.add(release)
        self.db.commit()
        return release

    def create_default_cluster(self):
        cluster = Cluster()
        cluster.name = u"cluster_name_" + str(randint(0, 100000000))
        cluster.release = self.create_default_release()
        self.db.add(cluster)
        self.db.commit()
        return cluster

    def create_cluster_api(self):
        resp = self.app.post(
            reverse('ClusterCollectionHandler'),
            json.dumps({
                'name': 'cluster-api-' + str(randint(0, 1000000)),
                'release': self.create_default_release().id
            }),
            headers=self.default_headers
        )
        self.assertEquals(resp.status, 201)
        return json.loads(resp.body)


def reverse(name, kwargs=None):
    urldict = dict(zip(urls[1::2], urls[::2]))
    url = urldict[name]
    urlregex = re.compile(url)
    for kwarg in urlregex.groupindex:
        if not kwarg in kwargs:
            raise KeyError("Invalid argument specified")
        url = re.sub(r"\(.+\)", str(kwargs[kwarg]), url, 1)
    url = re.sub(r"\??\$", "", url)
    return "/api" + url
