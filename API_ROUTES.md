# ACEest Web API Reference

This document provides a complete reference for all API routes in the ACEest web application, including HTTP methods, parameters, request/response types, and authentication requirements.

---

## Authentication
- **Session-based authentication** is used for most routes. Login is required for all client management and data modification endpoints.

---

## Endpoints

### Auth

#### `POST /login`
- **Description:** Login user
- **Request:**
  - `application/x-www-form-urlencoded`
    - `username` (string, required)
    - `password` (string, required)
- **Response:**
  - `302` Redirect to dashboard on success, or back to login on failure

#### `GET /login`
- **Description:** Login page (HTML)
- **Response:**
  - `200` HTML login form

#### `GET /logout`
- **Description:** Logout user
- **Response:**
  - `302` Redirect to login

---

### Client Management

#### `GET /`
- **Description:** Main dashboard (requires login)
- **Response:**
  - `200` HTML dashboard

#### `POST /`
- **Description:** Add new client (requires login)
- **Request:**
  - `application/x-www-form-urlencoded`
    - `name` (string)
    - `age` (integer)
    - `height` (number)
    - `weight` (number)
    - `program` (string)
    - `target_weight` (number)
    - `target_adherence` (integer)
    - `adherence` (integer)
    - `notes` (string)
    - `membership_expiry` (date string)
- **Response:**
  - `200` HTML dashboard

#### `GET /export_csv`
- **Description:** Export all clients as CSV
- **Response:**
  - `200` CSV file download

#### `GET /clients/data`
- **Description:** Get client names and adherence for charting
- **Response:**
  - `200` JSON `{ names: [string], adherence: [integer] }`

#### `GET /edit_client/{client_name}`
- **Description:** Get client edit form (requires login)
- **Path Parameter:**
  - `client_name` (string, required)
- **Response:**
  - `200` HTML form

#### `POST /edit_client/{client_name}`
- **Description:** Update client details (requires login)
- **Path Parameter:**
  - `client_name` (string, required)
- **Request:**
  - `application/x-www-form-urlencoded`
    - `age` (integer)
    - `height` (number)
    - `weight` (number)
    - `program` (string)
    - `target_weight` (number)
    - `target_adherence` (integer)
    - `adherence` (integer)
    - `notes` (string)
    - `calories` (integer)
    - `membership_expiry` (date string)
- **Response:**
  - `302` Redirect to dashboard

#### `POST /delete_client/{client_name}`
- **Description:** Delete a client (requires login)
- **Path Parameter:**
  - `client_name` (string, required)
- **Response:**
  - `302` Redirect to dashboard

#### `GET /export_pdf/{client_name}`
- **Description:** Export client report as PDF (requires login)
- **Path Parameter:**
  - `client_name` (string, required)
- **Response:**
  - `200` PDF file download

---

### Progress & Metrics

#### `POST /save_progress`
- **Description:** Save weekly progress for a client
- **Request:**
  - `application/x-www-form-urlencoded`
    - `progress_name` (string)
    - `progress_adherence` (integer)
- **Response:**
  - `302` Redirect to dashboard

#### `GET /progress_chart/{client_name}`
- **Description:** Get adherence progress chart for a client
- **Path Parameter:**
  - `client_name` (string, required)
- **Response:**
  - `200` HTML page with embedded chart image

#### `GET /weight_trend_chart/{client_name}`
- **Description:** Get weight trend chart for a client
- **Path Parameter:**
  - `client_name` (string, required)
- **Response:**
  - `200` HTML page with embedded chart image

#### `GET /bmi_info/{client_name}`
- **Description:** Calculate and show BMI info for a client
- **Path Parameter:**
  - `client_name` (string, required)
- **Response:**
  - `302` Redirect to dashboard with BMI info as flash message

#### `POST /log_metrics`
- **Description:** Log body metrics for a client
- **Request:**
  - `application/x-www-form-urlencoded`
    - `metrics_client_name` (string)
    - `metrics_date` (date string)
    - `metrics_weight` (number)
    - `metrics_waist` (number)
    - `metrics_bodyfat` (number)
- **Response:**
  - `302` Redirect to dashboard

---

### Workouts

#### `GET /workout_history/{client_name}`
- **Description:** Get workout history for a client
- **Path Parameter:**
  - `client_name` (string, required)
- **Response:**
  - `200` HTML page with workout history

#### `POST /log_workout`
- **Description:** Log a workout for a client
- **Request:**
  - `application/x-www-form-urlencoded`
    - `workout_client_name` (string)
    - `workout_date` (date string)
    - `workout_type` (string)
    - `workout_duration` (integer)
    - `workout_notes` (string)
- **Response:**
  - `302` Redirect to dashboard

---

## Security
- Most endpoints require a valid session cookie (login required).
- Login/logout endpoints are public.

---

## Response Types
- HTML: Most GET endpoints render HTML pages.
- JSON: `/clients/data` returns JSON for charting.
- File: `/export_csv` (CSV), `/export_pdf/{client_name}` (PDF)
- Redirect: Most POST endpoints redirect after action.

---

For a full machine-readable specification, see `openapi.yaml` in the project root.
