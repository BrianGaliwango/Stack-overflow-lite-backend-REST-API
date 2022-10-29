


def test_home_page():
  app = ('flask_test.cfg')
  with testpath.test_client() as test_client:
    response = test_client.get('/index')
    assert response.status_code == 200
    assert b'Flask user management' in response.data
    