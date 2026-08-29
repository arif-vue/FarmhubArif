# FarmHub API

FarmHub is a simplified farm management platform designed for an agritech company. It supports farm registration, farmer onboarding, cow enrollment, operational activity tracking, and milk production reporting with clear role-based authorization.

## Project purpose

The platform helps teams manage:

- farms and assigned agents
- farmer registrations and farm assignment
- dairy cows by farm and owner
- health, birth, vaccination, and general activity logging
- milk yield tracking and farm-level summaries

## Role model

The system defines three primary roles:

- Super Admin
  - full platform access
  - can create agents, farms, and farmers
  - can view all records across the system

- Agent
  - manages assigned farms only
  - onboards farmers under their farms
  - records and views farm-level data within assigned scope

- Farmer
  - belongs to one farm only
  - manages their own cows
  - logs daily milk production and lifecycle/health activities

Role-based access is enforced through the custom user model and permission logic in the API layer.

## Tech stack

- Python 3.14
- Django 6.1
- Django REST Framework
- djangorestframework-simplejwt
- SQLite (development default)

## Project structure

```text
FarmHub/
├── api/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── authentications/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── farmhub/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── .gitignore
├── manage.py
├── Farmhum.postman_collection.json
├── README.md
└── venv/
```

## Environment setup

Use the existing virtual environment created in the project folder:

```bash
cd /Users/arifhossain/Desktop/FarmHub
source venv/bin/activate
```

Install dependencies if needed:

```bash
pip install django djangorestframework djangorestframework-simplejwt
```

## Database setup

Run migrations:

```bash
python manage.py migrate
```

Create a super admin user:

```bash
python manage.py createsuperuser
```

When prompted, choose a username such as `admin` and assign a secure password.

## Start the server

```bash
python manage.py runserver 0.0.0.0:8000
```

The API is then available at:

- http://127.0.0.1:8000/auth/
- http://127.0.0.1:8000/api/

## Authentication flow

### 1. Register a farmer

Endpoint:

```http
POST /auth/register/
```

Request body:

```json
{
  "username": "farmer1",
  "email": "farmer1@example.com",
  "password": "StrongPass123!",
  "role": "farmer"
}
```

### 2. Log in

Endpoint:

```http
POST /auth/login/
```

Request body:

```json
{
  "username": "farmer1",
  "password": "StrongPass123!"
}
```

Successful response:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>",
  "user": {
    "id": 1,
    "username": "farmer1",
    "email": "farmer1@example.com",
    "role": "farmer"
  }
}
```

### 3. Use the access token

Add this header to all protected requests:

```http
Authorization: Bearer <access_token>
```

### 4. Refresh expired tokens

Endpoint:

```http
POST /auth/token/refresh/
```

Request body:

```json
{
  "refresh": "<refresh_token>"
}
```

### 5. View current user

Endpoint:

```http
GET /auth/me/
```

## API endpoint overview

### Authentication routes

- `POST /auth/register/`
- `POST /auth/users/` - super admin only
- `POST /auth/login/`
- `POST /auth/token/refresh/`
- `GET /auth/me/`

### Farm routes

- `GET /api/farms/`
- `POST /api/farms/`
- `GET /api/farms/<id>/`
- `PUT /api/farms/<id>/`
- `PATCH /api/farms/<id>/`
- `DELETE /api/farms/<id>/`
- `GET /api/farms/<id>/summary/`

### Farmer routes

- `GET /api/farmers/`
- `POST /api/farmers/`

### Cow routes

- `GET /api/cows/`
- `POST /api/cows/`

### Activity routes

- `GET /api/activities/`
- `POST /api/activities/`

### Milk routes

- `GET /api/milk/`
- `POST /api/milk/`
- `GET /api/milk/summary/`

## Request examples

### Create a farm

```http
POST /api/farms/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "Green Valley",
  "location": "Riverside",
  "agent": 2
}
```

### Assign a farmer to a farm

```http
POST /api/farmers/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "user": 3,
  "farm": 1
}
```

### Create a cow

```http
POST /api/cows/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "Buttercup",
  "tag_number": "COW-001",
  "breed": "Holstein",
  "farm": 1,
  "owner": 3,
  "date_of_birth": "2020-01-15",
  "notes": "Healthy cow"
}
```

### Create an activity

```http
POST /api/activities/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "cow": 1,
  "activity_type": "vaccination",
  "occurred_on": "2026-08-29",
  "description": "Vaccination completed"
}
```

### Record milk production

```http
POST /api/milk/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "cow": 1,
  "recorded_on": "2026-08-29",
  "quantity_liters": 18.5,
  "notes": "Morning milking"
}
```

### Milk summary

```http
GET /api/milk/summary/?farm_id=1&farmer_id=3&start_date=2026-08-01&end_date=2026-08-30
Authorization: Bearer <access_token>
```

Example response:

```json
{
  "total_quantity_liters": 120.5
}
```

## Access rules

- Super admin sees all records and can create users.
- Agents access only farms assigned to them.
- Farmers can only access their own cows, their farm, and their own milk/activity records.

## Testing

The project contains Django tests for the authentication and farm-domain flows.

Run:

```bash
python manage.py test
```

## Postman collection

A Postman collection is included at:

- `Farmhum.postman_collection.json`

This collection includes the required folders:

- farm
- farmer
- cow
- activity
- milk

## Notes

This project is built as a clean, readable DRF implementation with a custom user role model and farm-scoped access control. The design intentionally keeps the API simple, testable, and easy to extend for future production work.
