from django.test import TestCase
from django.test.client import Client

# Create your tests here.
class ExampleTestCase(TestCase):

    def test_ok(self):
        self.assertEquals(1, 1)
        with self.assertRaises(ZeroDivisionError):
            1 / 0

    def test_client(self):
        cli = Client()
        response = cli.get('/main/')
        self.assertEqual(200, response.status_code)
        self.assertEqual('ok', response.context['test_check'])