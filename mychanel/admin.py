from django.contrib import admin
from .models import (
    Category, BlogPost, Video, Course, CourseChapter,
    ChapterQuiz, FinalTest, CourseCompletion,
    Webinar, PaymentMethod, Payment
)

# ================
# Inline Admins
# ================

class ChapterQuizInline(admin.TabularInline):
    model = ChapterQuiz
    extra = 1


class CourseChapterInline(admin.TabularInline):
    model = CourseChapter
    extra = 1


class FinalTestInline(admin.TabularInline):
    model = FinalTest
    extra = 1


# ================
# Model Admins
# ================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'created_at', 'views')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'created_at', 'views')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    inlines = [CourseChapterInline, FinalTestInline]


@admin.register(CourseChapter)
class CourseChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order')
    list_filter = ('course',)
    ordering = ('course', 'order')
    search_fields = ('title',)
    inlines = [ChapterQuizInline]


@admin.register(ChapterQuiz)
class ChapterQuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter', 'question', 'correct_answer')
    list_filter = ('chapter',)
    search_fields = ('question',)


@admin.register(FinalTest)
class FinalTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'question', 'correct_answer')
    list_filter = ('course',)
    search_fields = ('question',)


@admin.register(CourseCompletion)
class CourseCompletionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'score', 'completed_at')
    list_filter = ('course', 'completed_at')
    search_fields = ('user__username', 'course__title')
    date_hierarchy = 'completed_at'


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date', 'price', 'link')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'payment_type', 'status', 'payment_method', 'date')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('user__username', 'payment_type')
    date_hierarchy = 'date'


