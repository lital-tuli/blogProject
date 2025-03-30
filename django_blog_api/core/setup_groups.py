# core/setup_groups.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from articles.models import Article
from comments.models import Comment

def create_user_groups():
    # Create groups
    editors_group, _ = Group.objects.get_or_create(name='editors')
    users_group, _ = Group.objects.get_or_create(name='users')
    management_group, _ = Group.objects.get_or_create(name='management')
    
    # Get content types
    article_content_type = ContentType.objects.get_for_model(Article)
    comment_content_type = ContentType.objects.get_for_model(Comment)
    
    # Get permissions
    article_permissions = Permission.objects.filter(content_type=article_content_type)
    comment_permissions = Permission.objects.filter(content_type=comment_content_type)
    
    # Set permissions for editors (can create/edit/delete articles)
    for perm in article_permissions:
        editors_group.permissions.add(perm)
    
    # Set permissions for management (can do everything)
    for perm in article_permissions:
        management_group.permissions.add(perm)
    for perm in comment_permissions:
        management_group.permissions.add(perm)
    
    # Set permissions for regular users (can add/edit their own comments)
    # Adding all comment permissions except delete
    for perm in comment_permissions:
        if perm.codename != 'delete_comment':
            users_group.permissions.add(perm)
    
    # Make sure view permissions for articles are added to users
    view_article_perm = Permission.objects.get(
        codename='view_article',
        content_type=article_content_type
    )
    users_group.permissions.add(view_article_perm)
    
    return {
        'editors': editors_group,
        'users': users_group,
        'management': management_group
    }