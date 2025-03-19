API Documentation


## Base URL
All endpoints are relative to: `http://localhost:8000/api/`

## Authentication

### Register a New User
- **URL:** `/auth/register/`
- **Method:** `POST`
- **Authentication:** None
- **Request Body:**
  ```json
  {
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "SecurePassword123"
  }

Success Response: 201 Created
jsonCopy{
  "user": {
    "id": 4,
    "username": "newuser",
    "email": "newuser@example.com"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}


Obtain JWT Token

URL: /auth/token/
Method: POST
Authentication: None
Request Body:
jsonCopy{
  "username": "user",
  "password": "user1234"
}

Success Response: 200 OK
jsonCopy{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}


Refresh JWT Token

URL: /auth/token/refresh/
Method: POST
Authentication: None
Request Body:
jsonCopy{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Success Response: 200 OK
jsonCopy{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}


Articles
List All Articles

URL: /articles/
Method: GET
Authentication: Optional
Query Parameters:

search: Search in title, content, tags, or author (e.g., /articles/?search=django)
tag: Filter by tag (e.g., /articles/?tag=python)
author: Filter by author username (e.g., /articles/?author=admin)
ordering: Order results (e.g., /articles/?ordering=-publication_date)
page: Pagination page number (e.g., /articles/?page=2)


Success Response: 200 OK
jsonCopy{
  "count": 10,
  "next": "http://localhost:8000/api/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "First Article",
      "content": "This is the content of the first article...",
      "author": 1,
      "author_username": "admin",
      "publication_date": "2023-07-15T10:30:45Z",
      "updated_at": "2023-07-15T10:30:45Z",
      "tags": ["django", "rest", "api"]
    },
    // More articles...
  ]
}


Get Single Article

URL: /articles/{id}/
Method: GET
Authentication: Optional
Success Response: 200 OK
jsonCopy{
  "id": 1,
  "title": "First Article",
  "content": "This is the content of the first article...",
  "author": 1,
  "author_username": "admin",
  "publication_date": "2023-07-15T10:30:45Z",
  "updated_at": "2023-07-15T10:30:45Z",
  "tags": ["django", "rest", "api"]
}


Create Article

URL: /articles/
Method: POST
Authentication: Required (Editor or Admin)
Headers:

Authorization: Bearer {access_token}


Request Body:
jsonCopy{
  "title": "New Article Title",
  "content": "Content of the new article...",
  "tags": ["tag1", "tag2"]
}

Success Response: 201 Created
jsonCopy{
  "id": 3,
  "title": "New Article Title",
  "content": "Content of the new article...",
  "author": 1,
  "author_username": "admin",
  "publication_date": "2023-07-16T14:25:30Z",
  "updated_at": "2023-07-16T14:25:30Z",
  "tags": ["tag1", "tag2"]
}


Update Article

URL: /articles/{id}/
Method: PUT
Authentication: Required (Editor or Admin)
Headers:

Authorization: Bearer {access_token}


Request Body:
jsonCopy{
  "title": "Updated Article Title",
  "content": "Updated content...",
  "tags": ["updated", "tags"]
}

Success Response: 200 OK

Delete Article

URL: /articles/{id}/
Method: DELETE
Authentication: Required (Editor or Admin)
Headers:

Authorization: Bearer {access_token}


Success Response: 204 No Content

Comments
List Comments for an Article

URL: /articles/{id}/comments/
Method: GET
Authentication: Optional
Success Response: 200 OK
jsonCopy[
  {
    "id": 1,
    "content": "Great article! Very informative and well-written.",
    "author": 3,
    "author_username": "user",
    "created_at": "2023-07-15T11:45:22Z",
    "updated_at": "2023-07-15T11:45:22Z",
    "article": 1,
    "reply_to": null
  },
  // More comments...
]


Add Comment to Article

URL: /articles/{id}/comments/
Method: POST
Authentication: Required
Headers:

Authorization: Bearer {access_token}


Request Body:
jsonCopy{
  "content": "This is my comment on the article."
}

Success Response: 201 Created
jsonCopy{
  "id": 3,
  "content": "This is my comment on the article.",
  "author": 3,
  "author_username": "user",
  "created_at": "2023-07-16T15:30:45Z",
  "updated_at": "2023-07-16T15:30:45Z",
  "article": 1,
  "reply_to": null
}


Get Single Comment

URL: /comments/{id}/
Method: GET
Authentication: Optional
Success Response: 200 OK
jsonCopy{
  "id": 1,
  "content": "Great article! Very informative and well-written.",
  "author": 3,
  "author_username": "user",
  "created_at": "2023-07-15T11:45:22Z",
  "updated_at": "2023-07-15T11:45:22Z",
  "article": 1,
  "reply_to": null
}


Update Comment

URL: /comments/{id}/
Method: PUT
Authentication: Required (Comment Owner Only)
Headers:

Authorization: Bearer {access_token}


Request Body:
jsonCopy{
  "content": "Updated comment content"
}

Success Response: 200 OK

Delete Comment

URL: /comments/{id}/
Method: DELETE
Authentication: Required (Admin or Comment Owner)
Headers:

Authorization: Bearer {access_token}


Success Response: 204 No Content

User Account
Get Current User Profile

URL: /auth/user/
Method: GET
Authentication: Required
Headers:

Authorization: Bearer {access_token}


Success Response: 200 OK
jsonCopy{
  "id": 3,
  "username": "user",
  "email": "user@example.com"
}


Status Codes

200 OK: The request was successful
201 Created: A new resource was successfully created
204 No Content: The request was successful but returns no content
400 Bad Request: The request was invalid or cannot be otherwise served
401 Unauthorized: Authentication failed or user doesn't have permissions
403 Forbidden: The request is understood, but it has been refused
404 Not Found: The requested resource does not exist
405 Method Not Allowed: The requested method is not supported for the resource
500 Internal Server Error: Something went wrong on the server