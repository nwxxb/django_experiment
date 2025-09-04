from app.models import User, UserRole

def test_user_create(client, db_session):
    request_data = {
            "username": "user", "email": "user@example.com", "role": UserRole.ADMIN.value, "password": "123"
    }
    # response = client.post("/api/users", json=request_data)
    response = client.post("/api/signup", json=request_data)

    user = db_session.query(User).filter_by(email="user@example.com").first()
    assert user.to_dict() == {"id": 1, "username": "user", "email": "user@example.com", "role": "admin"}
    assert response.status_code == 201
    assert response.json["user"] == {"id": 1, "username": "user", "email": "user@example.com", "role": "admin"}
    assert response.json["status"] == "created"

def test_user_show(client, db_session, user_factory, bearer_token_dict_factory):
    user = user_factory(username="user_1", email="user_1@example.com", role=UserRole.PATIENT)
    db_session.add(user)
    db_session.commit()

    headers = {} | bearer_token_dict_factory(user)
    response = client.get("/api/users/1", headers=headers)

    assert response.status_code == 200
    assert response.json["user"] == {"id": 1, "username": "user_1", "email": "user_1@example.com", "role": "patient"}
    assert response.json["status"] == "success"

def test_user_update(client, db_session, user_factory, bearer_token_dict_factory):
    user = user_factory(username="user_1", email="user_1@example.com", role=UserRole.PATIENT)
    db_session.add(user)
    db_session.commit()

    headers = {} | bearer_token_dict_factory(user)
    request_data = { "email": "new_user_1@example.com", "role": UserRole.DOCTOR.value }
    response = client.put("/api/users/1", json=request_data, headers=headers)

    user = db_session.get(User, 1)
    assert user.to_dict() == {"id": 1, "username": "user_1", "email": "new_user_1@example.com", "role": "doctor"}
    assert response.status_code == 200
    assert response.json["user"] == {"id": 1, "username": "user_1", "email": "new_user_1@example.com", "role": "doctor"}
    assert response.json["status"] == "updated"

def test_user_delete(client, db_session, user_factory, bearer_token_dict_factory):
    user = user_factory(username="user_1", email="user_1@example.com", role=UserRole.PATIENT)
    db_session.add(user)
    db_session.commit()

    headers = {} | bearer_token_dict_factory(user)
    response = client.delete("/api/users/1", headers=headers)

    user = db_session.get(User, 1)
    assert user is None
    assert response.status_code == 200
    assert response.json["user"] == {"id": 1, "username": "user_1", "email": "user_1@example.com", "role": "patient"}
    assert response.json["status"] == "deleted"
