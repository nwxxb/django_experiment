from app.models import User, UserRole, Service
from pytest_unordered import unordered

def test_services_create(client, db_session, user_factory):
    doctor = user_factory(username="doctor_1", email="doctor@example.com", role=UserRole.DOCTOR)
    db_session.add(doctor)
    db_session.commit()
    request_data = { "name": "A Therapy", "address": "RS Puri, West Jakarta", "doctor_id": doctor.id }
    response = client.post("/api/services", json=request_data)

    assert response.status_code == 201
    assert response.json["service"] == {
            "id": 1, "name": "A Therapy", "address": "RS Puri, West Jakarta",
            "doctor": {"id": doctor.id, "username": doctor.username, "email": doctor.email, "role": doctor.role.value}
        }
    assert response.json["status"] == "created"
    service = db_session.get(Service, 1)
    assert service.to_dict() == {
            "id": 1, "name": "A Therapy", "address": "RS Puri, West Jakarta",
            "doctor": {"id": doctor.id, "username": doctor.username, "email": doctor.email, "role": doctor.role.value}
        }

def test_services_index_all(client, db_session, service_factory, user_factory):
    doctor1 = user_factory(username="doctor1")
    doctor2 = user_factory(username="doctor2")
    services = [
        service_factory(name="Service 1", address="an address", doctor=doctor1),
        service_factory(name="Service 2", address="an address", doctor=doctor2),
        service_factory(name="Service 3", address="an address", doctor=doctor1),
        service_factory(name="Service 4", address="an address", doctor=doctor2),
        service_factory(name="Service 5", address="an address", doctor=doctor1),
        service_factory(name="Service 6", address="an address", doctor=doctor2)
    ]

    db_session.add_all(services)
    db_session.commit()

    response = client.get(f"/api/services")

    assert response.status_code == 200
    assert response.json["services"] == unordered([
            services[0].to_dict(), services[1].to_dict(),
            services[2].to_dict(), services[3].to_dict(),
            services[4].to_dict(), services[5].to_dict()
        ])
    assert response.json["status"] == "success"

def test_services_show(client, db_session, service_factory):
    service = service_factory(name="A Health Service", address="West Virginia")
    db_session.add(service)
    db_session.commit()

    response = client.get(f"/api/services/{service.id}")

    assert response.status_code == 200
    assert response.json["service"] == {
            "id": 1, "name": "A Health Service", "address": "West Virginia",
            "doctor": {"id": service.doctor.id, "username": service.doctor.username, "email": service.doctor.email, "role": service.doctor.role.value}
        }
    assert response.json["status"] == "success"

def test_service_update(client, db_session, service_factory, user_factory):
    new_doctor = user_factory(username="new_doctor", email="new_doctor@example.com", role=UserRole.DOCTOR)
    service = service_factory(name="A Health Service", address="West Virginia")
    db_session.add(service)
    db_session.add(new_doctor)
    db_session.commit()

    request_data = { "name": "A New Health Service", "address": "A New Address",  "doctor_id": new_doctor.id }
    response = client.put(f"/api/services/{service.id}", json=request_data)

    assert response.status_code == 200
    assert response.json["service"] == {
            "id": service.id, "name": "A New Health Service", "address": "A New Address",
            "doctor": {"id": new_doctor.id, "username": new_doctor.username, "email": new_doctor.email, "role": UserRole.DOCTOR.value}
        }
    assert response.json["status"] == "updated"
    service = db_session.get(Service, service.id)
    assert service.to_dict() == {
            "id": service.id, "name": "A New Health Service", "address": "A New Address",
            "doctor": {"id": new_doctor.id, "username": new_doctor.username, "email": new_doctor.email, "role": UserRole.DOCTOR.value}
        }
 
def test_service_delete(client, db_session, service_factory):
    service = service_factory(name="A Health Service", address="West Virginia")
    old_doctor = service.doctor
    db_session.add(service)
    db_session.commit()

    response = client.delete(f"/api/services/{service.id}")

    service = db_session.get(Service, service.id)
    assert service is None
    doctor = db_session.get(User, old_doctor.id)
    assert doctor is not None
    assert response.status_code == 200
    assert response.json["service"] == { "id": 1, "name": "A Health Service", "address": "West Virginia" }
    assert response.json["status"] == "deleted"
