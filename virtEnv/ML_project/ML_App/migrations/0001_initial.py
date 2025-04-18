# Generated by Django 5.1.4 on 2025-03-04 13:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('video', models.FileField(blank=True, null=True, upload_to='videos/')),
                ('course_content', models.TextField()),
                ('course_material', models.FileField(blank=True, null=True, upload_to='materials/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3')], default=1)),
                ('max_score', models.PositiveIntegerField(default=10, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='ML_App.course')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('course', 'order')},
            },
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('instructor_number', models.CharField(editable=False, max_length=10, unique=True)),
                ('department', models.CharField(choices=[('CS', 'Computer Science'), ('ECE', 'Electronics & Communication'), ('ME', 'Mechanical Engineering')], max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='instructor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_instructor', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_content', models.BooleanField(default=False)),
                ('completed_video', models.BooleanField(default=False)),
                ('completed_material', models.BooleanField(default=False)),
                ('last_accessed', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='ML_App.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='ML_App.assignment')),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='ML_App.question')),
            ],
        ),
        migrations.CreateModel(
            name='StudentAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='ML_App.assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'assignment')},
            },
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ML_App.question')),
                ('selected_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ML_App.choice')),
                ('student_assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='ML_App.studentassignment')),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='ML_App.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'course')},
            },
        ),
    ]
