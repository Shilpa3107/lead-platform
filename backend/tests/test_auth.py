def test_register_creates_user(client):
    response = client.post("/auth/register", json={
        "email": "newuser@test.com", "password": "testpass123", "role": "member"
    })
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newuser@test.com"
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_duplicate_email_rejected(client):
    client.post("/auth/register", json={"email": "dup@test.com", "password": "pass123", "role": "member"})
    response = client.post("/auth/register", json={"email": "dup@test.com", "password": "pass123", "role": "member"})
    assert response.status_code == 400


def test_login_correct_credentials_returns_token(client):
    client.post("/auth/register", json={"email": "login@test.com", "password": "correctpass", "role": "member"})
    response = client.post("/auth/login", json={"email": "login@test.com", "password": "correctpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json={"email": "wrongpass@test.com", "password": "correctpass", "role": "member"})
    response = client.post("/auth/login", json={"email": "wrongpass@test.com", "password": "WRONGpass"})
    assert response.status_code == 401


def test_member_cannot_create_lead(client):
    client.post("/auth/register", json={"email": "memberonly@test.com", "password": "pass123", "role": "member"})
    login = client.post("/auth/login", json={"email": "memberonly@test.com", "password": "pass123"})
    token = login.json()["access_token"]

    response = client.post(
        "/leads",
        json={"name": "Should Fail"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_member_cannot_see_others_leads(client):
    admin_reg = client.post("/auth/register", json={"email": "adminx@test.com", "password": "pass123", "role": "admin"})
    admin_login = client.post("/auth/login", json={"email": "adminx@test.com", "password": "pass123"})
    admin_token = admin_login.json()["access_token"]

    member_a_reg = client.post("/auth/register", json={"email": "memberA@test.com", "password": "pass123", "role": "member"})
    member_a_id = member_a_reg.json()["id"]

    member_b_reg = client.post("/auth/register", json={"email": "memberB@test.com", "password": "pass123", "role": "member"})
    member_b_login = client.post("/auth/login", json={"email": "memberB@test.com", "password": "pass123"})
    member_b_token = member_b_login.json()["access_token"]

    create_resp = client.post("/leads", json={"name": "Private Lead"}, headers={"Authorization": f"Bearer {admin_token}"})
    lead_id = create_resp.json()["id"]

    client.patch(f"/leads/{lead_id}", json={"assigned_to_id": member_a_id}, headers={"Authorization": f"Bearer {admin_token}"})

    response = client.get(f"/leads/{lead_id}", headers={"Authorization": f"Bearer {member_b_token}"})
    assert response.status_code == 404