from app.models import User, UserRole

def test_login(client, db_session):
    password = '1234abc'
    user = User(username="user_1", email="user_1@example.com", role=UserRole.PATIENT)
    user.set_password(password)
    db_session.add(user)
    db_session.commit()

    request_data = { "email": user.email, "password": password }
    response = client.post("/api/signin", json=request_data)

    assert response.status_code == 200
    assert response.json["user"] == {"id": 1, "username": "user_1", "email": "user_1@example.com", "role": "patient"}
    assert response.json["status"] == "signed-in"
    assert isinstance(response.json["access_token"], str)
