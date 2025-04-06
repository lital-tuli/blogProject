from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from articles.models import Article
from comments.models import Comment

def create_user_groups():
    """Create user groups with appropriate permissions"""
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
    
    # Clear existing permissions to start fresh
    editors_group.permissions.clear()
    users_group.permissions.clear()
    management_group.permissions.clear()
    
    # Set permissions for regular users (can view articles and add/view comments)
    add_comment_perm = Permission.objects.get(
        codename='add_comment',
        content_type=comment_content_type
    )
   
    view_comment_perm = Permission.objects.get(
        codename='view_comment',
        content_type=comment_content_type
    )
    change_comment_perm = Permission.objects.get(
        codename='change_comment',
        content_type=comment_content_type
    )
    view_article_perm = Permission.objects.get(
        codename='view_article',
        content_type=article_content_type
    )
    
    
    users_group.permissions.add(view_article_perm)
    users_group.permissions.add(add_comment_perm)
    users_group.permissions.add(view_comment_perm)
    users_group.permissions.add(change_comment_perm)
    
    # Set permissions for editors (can create/edit/delete articles)
    for perm in article_permissions:
        editors_group.permissions.add(perm)
    
    # Also allow editors to manage comments
    for perm in comment_permissions:
        editors_group.permissions.add(perm)

    # Set permissions for management (full access to everything)
    for perm in article_permissions:
        management_group.permissions.add(perm)
    for perm in comment_permissions:
        management_group.permissions.add(perm)

    return {
        'editors': editors_group,
        'users': users_group,
        'management': management_group
    }