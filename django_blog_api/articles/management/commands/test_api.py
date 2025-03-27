import requests
import json
import sys

BASE_URL = 'http://localhost:8000/api'
TOKEN = None

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_fail(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")

def test_registration():
    """Test user registration"""
    print_header("Testing User Registration")
    
    # Generate unique username to avoid conflicts
    import random
    random_num = random.randint(1000, 9999)
    username = f"testuser{random_num}"
    
    data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "TestPassword123",
        "password2": "TestPassword123"
    }
    
    url = f"{BASE_URL}/auth/register/"
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        print_success(f"Registration successful for user: {username}")
        response_data = response.json()
        print_info(f"User ID: {response_data['user'].get('id', 'N/A')}")
        print_info(f"Username: {response_data['user'].get('username', 'N/A')}")
        
        # Store tokens for subsequent tests
        global TOKEN
        TOKEN = response_data.get('access')
        print_info(f"Token: {TOKEN[:20]}...")
        
        return response_data
    else:
        print_fail(f"Registration failed with status code: {response.status_code}")
        try:
            print_info(f"Error: {response.json()}")
        except:
            print_info(f"Response: {response.text}")
        return None

def test_login(username="user", password="user1234"):
    """Test user login with regular user"""
    print_header("Testing User Login")
    
    data = {
        "username": username,
        "password": password
    }
    
    url = f"{BASE_URL}/auth/token/"
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        print_success("Login successful")
        print_info(f"Access Token: {response_data['access'][:20]}...")
        
        # Store tokens for subsequent tests
        global TOKEN
        TOKEN = response_data.get('access')
        
        return response_data
    else:
        print_fail(f"Login failed with status code: {response.status_code}")
        try:
            print_info(f"Error: {response.json()}")
        except:
            print_info(f"Response: {response.text}")
        return None

def test_login_admin():
    """Test login with admin credentials"""
    return test_login("admin", "admin1234")

def test_fetch_articles():
    """Test fetching articles"""
    print_header("Testing Article Listing")
    
    url = f"{BASE_URL}/articles/"
    response = requests.get(url)
    
    if response.status_code == 200:
        response_data = response.json()
        print_success("Articles fetched successfully")
        
        if 'results' in response_data:
            articles = response_data['results']
            count = response_data.get('count', len(articles))
        else:
            articles = response_data
            count = len(articles)
            
        print_info(f"Number of articles: {count}")
        
        if len(articles) > 0:
            print_info("First article:")
            print_info(f"  Title: {articles[0]['title']}")
            print_info(f"  Author: {articles[0].get('author_username', 'Unknown')}")
            if 'tags' in articles[0]:
                print_info(f"  Tags: {', '.join(articles[0]['tags'])}")
        
        return response_data
    else:
        print_fail(f"Failed to fetch articles with status code: {response.status_code}")
        try:
            print_info(f"Error: {response.json()}")
        except:
            print_info(f"Response: {response.text}")
        return None

def test_search_articles():
    """Test article search functionality"""
    print_header("Testing Article Search")
    
    # Test cases for different search parameters
    search_tests = [
        {"param": "search", "value": "django", "desc": "by keyword"},
        {"param": "tag", "value": "python", "desc": "by tag"},
        {"param": "author", "value": "admin", "desc": "by author"}
    ]
    
    for test in search_tests:
        param = test["param"]
        value = test["value"]
        desc = test["desc"]
        
        url = f"{BASE_URL}/articles/?{param}={value}"
        response = requests.get(url)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if 'results' in response_data:
                articles = response_data['results']
                count = response_data.get('count', len(articles))
            else:
                articles = response_data
                count = len(articles)
                
            print_success(f"Search {desc} '{value}' returned {count} articles")
        else:
            print_fail(f"Search {desc} failed with status code: {response.status_code}")
    
    return True

def test_create_article():
    """Test article creation (requires authentication)"""
    print_header("Testing Article Creation")
    
    if not TOKEN:
        print_fail("No authentication token available. Please login first.")
        return None
    
    # Create an article
    data = {
        "title": "Test Article via API Script",
        "content": "This is a test article created through our API testing script. It should demonstrate that article creation works correctly.",
        "tags": ["test", "api", "automation"]
    }
    
    url = f"{BASE_URL}/articles/"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print_info(f"Using token: {TOKEN[:20]}...")
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code in [201, 200]:
        response_data = response.json()
        print_success("Article created successfully")
        print_info(f"Article ID: {response_data.get('id', 'N/A')}")
        print_info(f"Title: {response_data.get('title', 'N/A')}")
        return response_data
    else:
        print_fail(f"Article creation failed with status code: {response.status_code}")
        try:
            print_info(f"Error: {response.json()}")
        except:
            print_info(f"Response: {response.text}")
            
        if response.status_code == 403:
            print_info("This is expected if you're not logged in as an admin or editor user.")
        
        return None

def test_add_comment(article_id=1):
    """Test adding a comment to an article"""
    print_header("Testing Comment Creation")
    
    if not TOKEN:
        print_fail("No authentication token available. Please login first.")
        return None
    
    data = {
        "content": "This is a test comment added via the API testing script."
    }
    
    url = f"{BASE_URL}/articles/{article_id}/comments/"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print_info(f"Using token: {TOKEN[:20]}...")
    print_info(f"URL: {url}")
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code in [201, 200]:
        response_data = response.json()
        print_success("Comment added successfully")
        print_info(f"Comment ID: {response_data.get('id', 'N/A')}")
        print_info(f"Content: {response_data.get('content', 'N/A')}")
        return response_data
    else:
        print_fail(f"Comment creation failed with status code: {response.status_code}")
        try:
            print_info(f"Error: {response.json()}")
        except:
            print_info(f"Response: {response.text}")
        return None

def run_all_tests():
    """Run all tests in sequence"""
    global TOKEN
    
    # Try to login with default credentials first
    login_result = test_login()
    
    # Test article listing and search (these don't need authentication)
    test_fetch_articles()
    test_search_articles()
    
    # Test comment creation on an existing article
    if TOKEN:
        test_add_comment(1)  # Try to add comment to article with ID 1
    else:
        print_fail("Skipping comment test - no valid token")
    
    # Login as admin to test article creation
    admin_login = test_login_admin()
    if admin_login and 'access' in admin_login:
        TOKEN = admin_login['access']
        article = test_create_article()
        
        # If article creation succeeded, try to comment on it
        if article and 'id' in article:
            test_add_comment(article['id'])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Individual test execution based on argument
        test_name = sys.argv[1]
        if test_name == "register":
            test_registration()
        elif test_name == "login":
            if len(sys.argv) > 3:
                test_login(sys.argv[2], sys.argv[3])
            else:
                test_login()
        elif test_name == "login_admin":
            test_login_admin()
        elif test_name == "articles":
            test_fetch_articles()
        elif test_name == "search":
            test_search_articles()
        elif test_name == "create":
            test_login_admin()  # Login as admin first
            test_create_article()
        elif test_name == "comment":
            test_login()  # Login as regular user
            test_add_comment()
        else:
            print_fail(f"Unknown test: {test_name}")
    else:
        # Run all tests
        run_all_tests()