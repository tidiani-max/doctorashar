from django.db import models
from django.conf import settings
from django.utils import timezone
from django.conf import settings

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Blog Post Model
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='blog_thumbnails/', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


# Video Model
class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


# Course Model
from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    material = models.FileField(upload_to='course_materials/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)  # ✅ added
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class Webinar(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    zoom_webinar_id = models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)  # ✅ added
    access_code = models.CharField(max_length=100, blank=True, null=True)  # ✅ Added access code

    def __str__(self):
        return self.title
    

# Payment Method Model
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


# Payment Model
# models.py

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=100)  # 'course' or 'webinar'
    item_id = models.PositiveIntegerField()  # NEW: to track which course/webinar
    status = models.CharField(max_length=50)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.amount} IDR via {self.payment_method.name}"

# models.py

class CourseChapter(models.Model):
    course = models.ForeignKey(Course, related_name='chapters', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.title} - Chapter {self.order}: {self.title}"


class ChapterQuiz(models.Model):
    chapter = models.ForeignKey(CourseChapter, related_name='quizzes', on_delete=models.CASCADE)
    question = models.CharField(max_length=300)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])

    def __str__(self):
        return f"Quiz for {self.chapter.title}"

from django.db import models
from django.conf import settings

class ChapterQuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.chapter.title} - {self.score}"



class FinalTest(models.Model):
    course = models.ForeignKey(Course, related_name='final_tests', on_delete=models.CASCADE)
    question = models.CharField(max_length=300)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])

    def __str__(self):
        return f"Final Test for {self.course.title}"


class CourseCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} completed {self.course.title}"
