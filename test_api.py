import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_registration():
    print("\n=== Testing User Registration ===")
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "password": "TestPassword123"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_login(username="testuser1", password="TestPassword123"):
    print("\n=== Testing User Login ===")
    url = f"{BASE_URL}/auth/token/"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    try:
        response_data = response.json()
        print(f"Response: {response_data}")
        return response_data
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        return {}

def test_articles(token=None):
    print("\n=== Testing Articles List ===")
    url = f"{BASE_URL}/articles/"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Number of articles: {len(response.json())}")
    return response.json()

def test_create_article(token):
    print("\n=== Testing Article Creation (Admin Only) ===")
    url = f"{BASE_URL}/articles/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Article Created via API",
        "content": "This is a test article created using our API testing script.",
        "tags": ["test", "api"]
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.status_code < 300 else response.text}")
    return response.json() if response.status_code < 300 else None

def test_create_comment(article_id, token):
    print("\n=== Testing Comment Creation ===")
    url = f"{BASE_URL}/articles/{article_id}/comments/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "content": "This is a test comment created using our API testing script."
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.status_code < 300 else response.text}")
    return response.json() if response.status_code < 300 else None

if __name__ == "__main__":
    # Test registration (only run once)
    # reg_data = test_registration()
    
    # Test login
    login_data = test_login()
    if 'access' in login_data:
        access_token = login_data['access']
        
        # Test listing articles
        articles = test_articles(access_token)
        
        # Test creating an article (will only work if user is admin)
        article = test_create_article(access_token)
        
        # If we successfully created an article, test commenting on it
        if article and 'id' in article:
            test_create_comment(article['id'], access_token)
        elif articles and len(articles) > 0:
            # Otherwise comment on the first existing article
            test_create_comment(articles[0]['id'], access_token)