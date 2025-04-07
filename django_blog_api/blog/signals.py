from django.contrib.auth.models import User, Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    """
    This function runs automatically after migrations are applied.
    It ensures default groups, users, articles, and comments exist.
    """
    # Only run once when the app is fully loaded
    if sender.name != "blog":
        return
        
    print("Creating initial data...")
    
    # Create groups
    group_names = ["admin", "editors", "users"]
    groups = {}
    
    for group_name in group_names:
        group, created = Group.objects.get_or_create(name=group_name)
        groups[group_name] = group
        if created:
            print(f"Created group: {group_name}")

    # Create users and assign to groups
    users_data = [
        {"username": "admin_user", "email": "admin@example.com", "password": "adminpassword", "group": "admin"},
        {"username": "editor_user", "email": "editor@example.com", "password": "editorpassword", "group": "editors"},
        {"username": "regular_user", "email": "user@example.com", "password": "userpassword", "group": "users"},
    ]

    users = {}
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            email=user_data["email"]
        )
        if created:
            user.set_password(user_data["password"])
            user.save()
            user.groups.add(groups[user_data["group"]])
            print(f"Created user: {user.username} in group {user_data['group']}")
        users[user_data["group"]] = user

    # Get model classes
    Article = apps.get_model('articles', 'Article')
    Comment = apps.get_model('comments', 'Comment')
    
    # Create sample articles
    articles_data = [
        {"title": "Admin's First Article", "content": "This is an article by the admin user.", "author": users["admin"]},
        {"title": "Editor's First Article", "content": "This is an article by the editor user.", "author": users["editors"]},
    ]
    
    created_articles = []
    for article_data in articles_data:
        article, created = Article.objects.get_or_create(
            title=article_data["title"],
            defaults={
                "content": article_data["content"],
                "author": article_data["author"]
            }
        )
        if created:
            article.tags.add("sample")
            print(f"Created article: {article.title}")
        created_articles.append(article)

    # Create sample comments
    for article in created_articles:
        for user in users.values():
            comment, created = Comment.objects.get_or_create(
                article=article,
                author=user,
                content=f"This is a comment by {user.username} on the article '{article.title}'."
            )
            if created:
                print(f"Created comment by {user.username} on article: {article.title}")