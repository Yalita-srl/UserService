# User Service Microservice

This project is a simple, locally executable User Service for a delivery platform, built with Python, Django, and GraphQL. It provides basic CRUD functionality for users, JWT-based authentication, and role-based authorization.

## Features

-   **User Management**: Create, read, update, and delete users.
-   **Authentication**: JWT-based login with token refresh capabilities.
-   **Authorization**: Role-based access control for `user`, `admin`, and `restaurant_owner` roles.
-   **API**: 100% GraphQL API (no REST).
-   **Documentation**: Interactive GraphiQL interface to explore and test the API.

---

## Setup and Installation

### 1. Prerequisites

-   Python 3.8+
-   A running MySQL server instance.
-   `pip` and `venv` for managing Python packages.

### 2. Clone the Repository

First, get the project code on your local machine.
```bash
# This step is already done if you are reading this file in the project directory.
# git clone <repository-url>
# cd user-service
```

### 3. Install Dependencies

Install all the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (`user-service/`) by copying the example file.

```bash
# For Windows
copy .env.example .env

# For macOS/Linux
# cp .env.example .env
```

Now, open the `.env` file and fill in your specific configuration details, especially your database credentials and a new Django `SECRET_KEY`.

```ini
# .env

# Generate a new secret key. You can use an online generator.
SECRET_KEY=your-super-secret-key-here

# Your MySQL database configuration
DB_NAME=pedidos_user_service
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Development mode
DEBUG=1
```

### 5. Set Up the MySQL Database

Log in to your MySQL server and create a new database for the service.

```sql
CREATE DATABASE pedidos_user_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Run Database Migrations

Apply the database schema to your newly created database.

```bash
python manage.py migrate
```

### 7. Create a Superuser (Admin)

To test admin-only functionalities, create a superuser. You will be prompted to enter an email, name, and password.

```bash
python manage.py createsuperuser
```

### 8. Run the Development Server

Start the Django development server.

```bash
python manage.py runserver
```

The server will be running at `http://127.0.0.1:8000/`.

---

## How to Test the API

Navigate to the interactive GraphiQL interface at **[http://127.0.0.1:8000/graphql](http://127.0.0.1:8000/graphql)**.

### 1. Register a New User

```graphql
mutation {
  registerUser(input: {
    email: "testuser@example.com",
    password: "strongpassword123",
    name: "Test User",
    phone: "1234567890",
    address: "123 Main St",
    role: "user"
  }) {
    user {
      id
      email
      name
      role
    }
  }
}
```

### 2. Log In and Get a JWT

Use the credentials of the user you just created or the superuser.

```graphql
mutation {
  tokenAuth(email: "valeriaalexandracuellarcoca@gmail.com", password: "2529") {
    token
    user{
      id
      email
      name
      role
    }
  }
}

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMSIsImVtYWlsIjoidmFsZXJpYWFsZXhhbmRyYWN1ZWxsYXJjb2NhQGdtYWlsLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2MzAwNTU0OCwib3JpZ19pYXQiOjE3NjMwMDE5NDh9.3w61u3W276q_1C_mQD8ytcWw7g0j5BVSGpOpkF4g5iU
```
**Response:**
```json
{
  "data": {
    "tokenAuth": {
      "token": "eyJ0eXAiOiJKV1...",
      "refreshToken": "eyJ0eXAiOiJKV1..."
    }
  }
}
```

### 3. Make Authenticated Requests

To perform authenticated actions, you need to pass the received `token` in the HTTP headers. In the GraphiQL interface, open the "HTTP HEADERS" panel at the bottom and add:

```json
{
  "Authorization": "JWT eyJ0eXAiOiJKV1..."
}
```
*(Replace the token with the one you received)*

### 4. Get a User's Profile (Authenticated)

Get the profile of the user with ID `1`.

```graphql
query {
  user(id: "1") {
    id
    name
    email
    phone
    address
    role
  }
}
```

### 5. List All Users (Admin Only)

This query will only work if you are authenticated as an admin (the superuser you created).

```graphql
query {
  users(page: 1, limit: 5) {
    id
    email
    name
    role
  }
}
```

### 6. Delete a User (Admin Only)

This mutation will only work if you are authenticated as an admin.

```graphql
mutation {
  deleteUser(id: "2") {
    success
    id
  }
}
```

### 7. Run Unit Tests

To ensure everything is working as expected, you can run the built-in unit tests.

```bash
python manage.py test users
```
