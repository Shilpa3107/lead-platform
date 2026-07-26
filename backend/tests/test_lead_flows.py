def register_and_login(client, email, password, role):
    client.post("/auth/register", json={"email": email, "password": password, "role": role})
    login = client.post("/auth/login", json={"email": email, "password": password})
    return login.json()["access_token"]


def test_full_lead_lifecycle_flow(client):
    admin_token = register_and_login(client, "flowadmin@test.com", "pass123", "admin")
    member_reg = client.post("/auth/register", json={"email": "flowmember@test.com", "password": "pass123", "role": "member"})
    member_id = member_reg.json()["id"]
    member_token = client.post("/auth/login", json={"email": "flowmember@test.com", "password": "pass123"}).json()["access_token"]

    # Create
    create_resp = client.post("/leads", json={"name": "Flow Test Lead"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201
    lead_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "new"

    # Assign
    assign_resp = client.patch(f"/leads/{lead_id}", json={"assigned_to_id": member_id}, headers={"Authorization": f"Bearer {admin_token}"})
    assert assign_resp.status_code == 200
    assert assign_resp.json()["assigned_to_id"] == member_id

    # Member sees it
    list_resp = client.get("/leads", headers={"Authorization": f"Bearer {member_token}"})
    assert list_resp.json()["total"] == 1

    # Member changes status
    status_resp = client.patch(f"/leads/{lead_id}", json={"status": "contacted"}, headers={"Authorization": f"Bearer {member_token}"})
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "contacted"

    # Member adds a note
    note_resp = client.post(f"/leads/{lead_id}/notes", json={"content": "Test note"}, headers={"Authorization": f"Bearer {member_token}"})
    assert note_resp.status_code == 201
    assert note_resp.json()["author_id"] == member_id

    # Activity trail reflects everything
    activity_resp = client.get(f"/leads/{lead_id}/activity", headers={"Authorization": f"Bearer {member_token}"})
    actions = [entry["action"] for entry in activity_resp.json()]
    assert "created" in actions
    assert "assigned" in actions
    assert "status_changed" in actions
    assert "note_added" in actions


def test_public_capture_ignores_privileged_fields(client):
    response = client.post("/public/leads", json={
        "name": "Public Submitter",
        "status": "won",
        "assigned_to_id": "00000000-0000-0000-0000-000000000000",
    })
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "new"
    assert body["assigned_to_id"] is None


def test_public_capture_requires_no_auth(client):
    # no Authorization header at all
    response = client.post("/public/leads", json={"name": "No Auth Needed"})
    assert response.status_code == 201