from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from articles.models import Article
from comments.models import Comment

def create_user_groups():
    # Create admin group
    admin_group, created = Group.objects.get_or_create(name='admin_users')
    
    # Create regular users group
    regular_group, created = Group.objects.get_or_create(name='regular_users')
    
    # Get content types
    article_content_type = ContentType.objects.get_for_model(Article)
    comment_content_type = ContentType.objects.get_for_model(Comment)
    
    # Set permissions for admin users
    article_permissions = Permission.objects.filter(content_type=article_content_type)
    comment_permissions = Permission.objects.filter(content_type=comment_content_type)
    
    for perm in article_permissions:
        admin_group.permissions.add(perm)
    
    for perm in comment_permissions:
        admin_group.permissions.add(perm)
    
    # Set permissions for regular users
    comment_add_perm = Permission.objects.get(
        codename='add_comment',
        content_type=comment_content_type
    )
    comment_change_perm = Permission.objects.get(
        codename='change_comment',
        content_type=comment_content_type
    )
    
    regular_group.permissions.add(comment_add_perm)
    regular_group.permissions.add(comment_change_perm)