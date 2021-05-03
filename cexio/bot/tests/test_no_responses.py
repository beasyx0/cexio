from django.test import TestCase


class TestNoResponses(TestCase):
    '''Test that there is nothing found when visiting the domain'''

    def test_send_post_root(self):

        print('Testing no root post response')

        r = self.client.post('/')
        self.assertEqual(r.status_code, 404)

        print('Testing complete')

    def test_send_post_login(self):

        print('Testing no login post response')

        r = self.client.post('/login')
        self.assertEqual(r.status_code, 404)

        print('Testing complete')

    def test_get_root(self):

        print('Testing no root get response')

        r = self.client.get('/')
        self.assertEqual(r.status_code, 404)

        print('Testing complete')

    def test_get_login(self):

        print('Testing no login get response')

        r = self.client.get('/login')
        self.assertEqual(r.status_code, 404)

        print('Testing complete')
