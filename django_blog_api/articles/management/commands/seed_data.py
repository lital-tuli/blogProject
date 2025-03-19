from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from articles.models import Article
from comments.models import Comment
from core.setup_groups import create_user_groups
from django.db import transaction

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create user groups
        groups = create_user_groups()
        
        # Create admin user (management)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            email='admin@example.com',
            defaults={
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin1234')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')
        
        admin_user.groups.add(groups['management'])
        
        # Create editor user
        editor_user, created = User.objects.get_or_create(
            username='editor',
            email='editor@example.com'
        )
        
        if created:
            editor_user.set_password('editor1234')
            editor_user.save()
            self.stdout.write(f'Created editor user: {editor_user.username}')
        
        editor_user.groups.add(groups['editors'])
        
        # Create regular user
        regular_user, created = User.objects.get_or_create(
            username='user',
            email='user@example.com'
        )
        
        if created:
            regular_user.set_password('user1234')
            regular_user.save()
            self.stdout.write(f'Created regular user: {regular_user.username}')
        
        regular_user.groups.add(groups['users'])
        
        # Create sample articles
        article1, created = Article.objects.get_or_create(
            title='First Article',
            defaults={
                'content': 'This is the content of the first article. It covers various topics related to Django and REST framework.',
                'author': admin_user
            }
        )
        
        if created:
            article1.tags.add('django', 'rest', 'api')
            self.stdout.write(f'Created article: {article1.title}')
        
        article2, created = Article.objects.get_or_create(
            title='Second Article',
            defaults={
                'content': 'This is the content of the second article. It discusses advanced topics in web development with Python.',
                'author': admin_user
            }
        )
        
        if created:
            article2.tags.add('python', 'advanced', 'web')
            self.stdout.write(f'Created article: {article2.title}')
        
        # Create sample comments
        comment1, created = Comment.objects.get_or_create(
            author=regular_user,
            article=article1,
            content='Great article! Very informative and well-written.'
        )
        
        if created:
            self.stdout.write(f'Created comment on article: {article1.title}')
        
        comment2, created = Comment.objects.get_or_create(
            author=regular_user,
            article=article2,
            content='Thanks for sharing this information!'
        )
        
        if created:
            self.stdout.write(f'Created comment on article: {article2.title}')
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))