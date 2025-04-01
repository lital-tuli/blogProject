# Django Blog API

A full-featured blog API built with Django REST Framework, featuring a React frontend for a complete blog application.

## Project Overview

This project implements a blog platform where users can register, create articles, and engage with content through comments. The system features different user roles (regular users, editors, and management) with appropriate permissions for each.

## Features

- **User Authentication**: JWT-based authentication with token refresh
- **Articles Management**: Create, read, update, and delete blog articles
- **Comments System**: Add comments to articles with nested replies
- **Search & Filtering**: Search articles by title, content, tags, or author
- **User Roles**: Different permission levels for different user types
- **React Frontend**: Modern responsive UI built with React and Bootstrap

## Technology Stack

### Backend
- Django 5.1
- Django REST Framework
- PostgreSQL
- Simple JWT for authentication
- Django Filter for filtering capabilities
- Django CORS Headers for frontend communication
- Taggit for article tagging

### Frontend
- React 19
- Redux Toolkit for state management
- React Router for navigation
- Formik & Yup for form handling and validation
- Axios for API requests
- Bootstrap 5 for responsive design

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Articles
- `GET /api/articles/` - List all articles
- `GET /api/articles/?search=<query>` - Search articles by title, content, tags, or author
- `GET /api/articles/<id>/` - Get specific article details
- `POST /api/articles/` - Create a new article (admin/editor only)
- `PUT /api/articles/<id>/` - Update an article (admin/editor only)
- `DELETE /api/articles/<id>/` - Delete an article (admin/editor only)

### Comments
- `GET /api/articles/<id>/comments/` - Get all comments for an article
- `POST /api/articles/<id>/comments/` - Add a comment to an article (authenticated users)
- `DELETE /api/comments/<id>/` - Delete a comment (admin only)

## User Roles and Permissions

- **Regular Users**:
  - Can register and login
  - Can view articles
  - Can add comments

- **Editors**:
  - Can create, edit, and delete articles
  - Can add comments

- **Management**:
  - Full administrative access
  - Can delete any comments

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/django-blog-api.git
   cd django-blog-api
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DB_NAME=blog_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Seed the database with initial data:
   ```
   python manage.py seed_data
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd ../blog-frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

## Default User Accounts

After running the seed command, the following user accounts are available for testing:

1. Admin User:
   - Username: admin
   - Password: admin1234
   - Role: Management

2. Editor User:
   - Username: editor
   - Password: editor1234
   - Role: Editor

3. Regular User:
   - Username: user
   - Password: user1234
   - Role: Regular User

## Project Structure

### Backend

```
django_blog_api/
├── articles/              # Articles app
│   ├── models.py          # Article model
│   ├── serializers.py     # Article serializer
│   ├── views.py           # Article views
│   └── urls.py            # Article URLs
├── comments/              # Comments app
│   ├── models.py          # Comment model
│   ├── serializers.py     # Comment serializer
│   ├── views.py           # Comment views
│   └── urls.py            # Comment URLs
├── core/                  # Core functionality
│   ├── permissions.py     # Custom permission classes
│   └── setup_groups.py    # User group setup
├── users/                 # User authentication
├── /          # Project settings
└── manage.py              # Django management script
```

### Frontend

```
blog-frontend/
├── src/
│   ├── components/        # Reusable components
│   │   ├── articles/      # Article components
│   │   ├── comments/      # Comment components
│   │   ├── common/        # Common components
│   │   └── layout/        # Layout components
│   ├── pages/             # Page components
│   ├── services/          # API service
│   ├── store/             # Redux store
│   │   ├── articlesSlice.js
│   │   ├── authSlice.js
│   │   ├── commentsSlice.js
│   │   └── index.js
│   ├── context/           # React context
│   ├── hooks/             # Custom hooks
│   └── App.jsx            # Main app component
└── index.html             # HTML entry point
```

## Development Guidelines

- Clean, organized code with meaningful names
- Modules limited to under 200 lines of code
- Consistent coding style following PEP 8 for Python and ESLint for JavaScript
- Environment variables for sensitive configuration
- Proper error handling and validation

## Credits

This project was developed as a final module project for the Django course.
