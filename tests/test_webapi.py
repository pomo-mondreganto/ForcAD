from unittest import TestCase

import requests


class WebApiTestCase(TestCase):
    def testScoreboardPage(self):
        r = requests.get('http://127.0.0.1:8080/')
        self.assertTrue(r.ok)
