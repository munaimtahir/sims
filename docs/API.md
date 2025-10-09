# SIMS API Documentation

This document describes the RESTful API endpoints available in the SIMS application.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Common Response Formats](#common-response-formats)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
  - [User Management](#user-management)
  - [Logbook](#logbook)
  - [Cases](#cases)
  - [Certificates](#certificates)
  - [Rotations](#rotations)

## Overview

### Base URL

```
Development: http://127.0.0.1:8000
Production: https://your-domain.com
```

### API Version

Current Version: `v1` (implicit in URLs)

### Content Type

All requests and responses use JSON format:
```
Content-Type: application/json
```

## Authentication

Most API endpoints require authentication using Django's session authentication.

### Login Required

Endpoints marked with 🔒 require user authentication. If not authenticated, the API will return a 401 or redirect to login.

### Permission Requirements

- 👤 **User**: Authenticated user
- 👨‍💼 **Supervisor**: Supervisor role required
- 👑 **Admin**: Admin role required

## Common Response Formats

### Success Response

```json
{
    "status": "success",
    "data": {
        // Response data here
    },
    "message": "Optional success message"
}
```

### List Response with Pagination

```json
{
    "status": "success",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 25
    }
}
```

## Error Handling

### Error Response Format

```json
{
    "status": "error",
    "message": "Human-readable error message",
    "code": "ERROR_CODE",
    "details": {
        // Optional additional error details
    }
}
```

### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## API Endpoints

### User Management

#### Get User Statistics

Get statistical information about users.

**Endpoint:** `GET /users/api/stats/`

**Authentication:** 🔒 Required (Admin)

**Response:**
```json
{
    "status": "success",
    "data": {
        "total_users": 150,
        "active_users": 145,
        "by_role": {
            "pg": 120,
            "supervisor": 20,
            "admin": 5
        },
        "new_this_month": 10
    }
}
```

---

### Logbook

#### Get Logbook Statistics

Retrieve statistics for logbook entries.

**Endpoint:** `GET /logbook/api/stats/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `pg_id` (optional): Filter by postgraduate user ID
- `period` (optional): Time period (`week`, `month`, `year`, `all`)
- `supervisor_id` (optional): Filter by supervisor

**Response:**
```json
{
    "status": "success",
    "data": {
        "total_entries": 250,
        "pending_review": 15,
        "approved": 220,
        "rejected": 5,
        "by_category": {
            "procedure": 150,
            "observation": 80,
            "study": 20
        },
        "completion_rate": 88.5
    }
}
```

#### Update Logbook Statistics

Trigger statistics recalculation for logbook entries.

**Endpoint:** `POST /logbook/api/update-stats/`

**Authentication:** 🔒 Required

**Request Body:**
```json
{
    "pg_id": 123,
    "force_recalculate": true
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Statistics updated successfully",
    "data": {
        "entries_processed": 250,
        "updated_at": "2025-01-15T10:30:00Z"
    }
}
```

#### Export Logbook Entries

Export logbook entries to CSV format.

**Endpoint:** `GET /logbook/export/csv/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `pg_id` (optional): Filter by postgraduate user ID
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:** CSV file download

#### Get Template Preview

Get preview data for a logbook entry template.

**Endpoint:** `GET /logbook/api/template/<int:template_id>/preview/`

**Authentication:** 🔒 Required

**Response:**
```json
{
    "status": "success",
    "data": {
        "template_id": 5,
        "name": "Surgical Procedure Template",
        "fields": [
            {
                "name": "procedure_name",
                "type": "text",
                "required": true
            },
            {
                "name": "duration",
                "type": "number",
                "required": true
            }
        ]
    }
}
```

#### Get Entry Complexity

Calculate complexity score for a logbook entry.

**Endpoint:** `GET /logbook/api/entry/<int:entry_id>/complexity/`

**Authentication:** 🔒 Required

**Response:**
```json
{
    "status": "success",
    "data": {
        "entry_id": 123,
        "complexity_score": 7.5,
        "factors": {
            "duration": 3,
            "techniques_used": 4,
            "complications": 2
        },
        "level": "advanced"
    }
}
```

---

### Cases

#### Get Case Statistics

Retrieve statistics for clinical cases.

**Endpoint:** `GET /cases/statistics/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `pg_id` (optional): Filter by postgraduate user ID
- `status` (optional): Filter by case status

**Response:**
```json
{
    "status": "success",
    "data": {
        "total_cases": 180,
        "by_status": {
            "pending": 25,
            "approved": 140,
            "rejected": 15
        },
        "by_category": {
            "surgical": 90,
            "medical": 70,
            "emergency": 20
        },
        "average_review_time": 2.5
    }
}
```

#### Export Case Data

Export clinical cases to CSV format.

**Endpoint:** `GET /cases/export/`

**Authentication:** 🔒 Required (Supervisor or Admin)

**Query Parameters:**
- `pg_id` (optional): Filter by postgraduate user ID
- `category` (optional): Filter by case category
- `start_date` (optional): Start date filter

**Response:** CSV file download

#### Get Diagnoses (JSON)

Get list of available diagnoses for autocomplete.

**Endpoint:** `GET /cases/api/diagnoses/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `q` (optional): Search query

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "name": "Appendicitis",
            "code": "K35.80"
        },
        {
            "id": 2,
            "name": "Cholecystitis",
            "code": "K81.0"
        }
    ]
}
```

#### Get Procedures (JSON)

Get list of available procedures for autocomplete.

**Endpoint:** `GET /cases/api/procedures/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `q` (optional): Search query

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "name": "Appendectomy",
            "code": "44950"
        },
        {
            "id": 2,
            "name": "Cholecystectomy",
            "code": "47562"
        }
    ]
}
```

---

### Certificates

#### Get Certificate Statistics

Retrieve statistics for certificates.

**Endpoint:** `GET /certificates/api/stats/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `pg_id` (optional): Filter by postgraduate user ID

**Response:**
```json
{
    "status": "success",
    "data": {
        "total_certificates": 45,
        "active": 40,
        "expired": 5,
        "by_type": {
            "course": 20,
            "workshop": 15,
            "conference": 10
        },
        "compliance_rate": 88.9
    }
}
```

#### Get Quick Stats

Get quick statistics for certificates.

**Endpoint:** `GET /certificates/api/quick-stats/`

**Authentication:** 🔒 Required

**Response:**
```json
{
    "status": "success",
    "data": {
        "total": 45,
        "expiring_soon": 5,
        "recently_added": 3
    }
}
```

#### Verify Certificate

Verify authenticity of a certificate.

**Endpoint:** `GET /certificates/api/<int:pk>/verify/`

**Authentication:** 🔒 Required

**Response:**
```json
{
    "status": "success",
    "data": {
        "certificate_id": 123,
        "is_valid": true,
        "issued_to": "John Doe",
        "issued_date": "2024-01-15",
        "expiry_date": "2026-01-15",
        "status": "active"
    }
}
```

#### Export Certificates

Export certificates to CSV format.

**Endpoint:** `GET /certificates/export/csv/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `pg_id` (optional): Filter by postgraduate user ID
- `status` (optional): Filter by status

**Response:** CSV file download

---

### Rotations

#### Get Rotation Statistics

Retrieve statistics for rotations.

**Endpoint:** `GET /rotations/api/stats/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `pg_id` (optional): Filter by postgraduate user ID
- `department` (optional): Filter by department

**Response:**
```json
{
    "status": "success",
    "data": {
        "total_rotations": 60,
        "active": 15,
        "completed": 40,
        "planned": 5,
        "by_department": {
            "surgery": 20,
            "medicine": 25,
            "pediatrics": 15
        },
        "average_duration": 8
    }
}
```

#### Get Quick Stats

Get quick statistics for rotations.

**Endpoint:** `GET /rotations/api/quick-stats/`

**Authentication:** 🔒 Required

**Response:**
```json
{
    "status": "success",
    "data": {
        "active_rotations": 15,
        "upcoming": 5,
        "completion_rate": 95.2
    }
}
```

#### Get Calendar Data

Get rotation data formatted for calendar display.

**Endpoint:** `GET /rotations/api/calendar/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `start` (optional): Start date (YYYY-MM-DD)
- `end` (optional): End date (YYYY-MM-DD)
- `pg_id` (optional): Filter by postgraduate user ID

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "title": "Surgery Rotation - John Doe",
            "start": "2025-01-15",
            "end": "2025-03-15",
            "color": "#007bff",
            "department": "Surgery",
            "pg_name": "John Doe"
        }
    ]
}
```

#### Get Departments by Hospital

Get list of departments for a specific hospital.

**Endpoint:** `GET /rotations/api/departments/<int:hospital_id>/`

**Authentication:** 🔒 Required

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "name": "Surgery",
            "capacity": 10
        },
        {
            "id": 2,
            "name": "Medicine",
            "capacity": 15
        }
    ]
}
```

#### Export Rotations

Export rotations to CSV format.

**Endpoint:** `GET /rotations/export/csv/`

**Authentication:** 🔒 Required

**Query Parameters:**
- `pg_id` (optional): Filter by postgraduate user ID
- `department` (optional): Filter by department
- `status` (optional): Filter by status

**Response:** CSV file download

---

## Rate Limiting

Currently, there are no rate limits enforced. However, for production deployment, consider implementing rate limiting to prevent abuse.

## Versioning

The API does not currently use explicit versioning. Future versions may introduce `/api/v2/` endpoints.

## Changelog

### Version 1.0 (January 2025)
- Initial API documentation
- All core endpoints documented
- Statistics and export endpoints

---

## Examples

### Using cURL

```bash
# Get logbook statistics
curl -X GET "http://127.0.0.1:8000/logbook/api/stats/" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -H "Content-Type: application/json"

# Export cases to CSV
curl -X GET "http://127.0.0.1:8000/cases/export/?pg_id=123" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  --output cases.csv
```

### Using Python Requests

```python
import requests

# Login first
session = requests.Session()
session.post('http://127.0.0.1:8000/accounts/login/', {
    'username': 'admin',
    'password': 'admin123'
})

# Get statistics
response = session.get('http://127.0.0.1:8000/logbook/api/stats/')
data = response.json()
print(data)

# Export to CSV
response = session.get('http://127.0.0.1:8000/cases/export/')
with open('cases.csv', 'wb') as f:
    f.write(response.content)
```

### Using JavaScript (Fetch API)

```javascript
// Get statistics
fetch('/logbook/api/stats/')
    .then(response => response.json())
    .then(data => {
        console.log('Logbook Stats:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });

// Post data
fetch('/logbook/api/update-stats/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        pg_id: 123,
        force_recalculate: true
    })
})
.then(response => response.json())
.then(data => console.log(data));

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

---

For questions or issues with the API, please contact the development team or open an issue on GitHub.
