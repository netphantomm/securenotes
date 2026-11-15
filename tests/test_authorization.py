def test_anonymous_user_is_redirected_to_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"
