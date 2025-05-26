

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings



from .models import BlogPost, Video, Course, Webinar, Category


from django.utils.timezone import now

def home(request):
    query = request.GET.get("q")
    category = request.GET.get("category")

    blogs = BlogPost.objects.all().order_by('-created_at')

    if query:
        blogs = blogs.filter(Q(title__icontains=query) | Q(content__icontains=query))
    if category:
        blogs = blogs.filter(category__name__iexact=category)

    # Paginate blogs (3 per page)
    paginator = Paginator(blogs, 3)
    page_number = request.GET.get("page")
    blog_page = paginator.get_page(page_number)

    # Always show latest 2 upcoming webinars
    webinars = Webinar.objects.filter(date__gte=now()).order_by('date')[:3]

    # Always show latest 3 videos
    videos = Video.objects.all().order_by('-created_at')[:3]

    # Always show latest 2 courses
    courses = Course.objects.all().order_by('-created_at')[:3]

    context = {
        'blogs': blog_page,
        'categories': Category.objects.all(),
        'videos': videos,
        'courses': courses,
        'webinars': webinars,
        'query': query,
        'selected_category': category,
    }

    if request.user.is_authenticated:
        paid_courses = list(Payment.objects.filter(
            user=request.user,
            payment_type__iexact="course",
            status__iexact="Completed"
        ).values_list('item_id', flat=True))

        paid_webinars = list(Payment.objects.filter(
            user=request.user,
            payment_type__iexact="webinar",
            status__iexact="Completed"
        ).values_list('item_id', flat=True))

        # Convert IDs to integers
        paid_courses = [int(id) for id in paid_courses]
        paid_webinars = [int(id) for id in paid_webinars]
    else:
        paid_courses = []
        paid_webinars = []

    context.update({
        'paid_courses': paid_courses,
        'paid_webinars': paid_webinars,
    })

    return render(request, 'home.html', context)





from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import BlogPost,Video,Course,Webinar

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import BlogPost, Video, Course, Webinar, Category

def edit_blog(request, blog_id):
    blog = get_object_or_404(BlogPost, id=blog_id)
    categories = Category.objects.all()

    if request.method == "POST":
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.category_id = request.POST.get('category') or None
        if 'thumbnail' in request.FILES:
            blog.thumbnail = request.FILES['thumbnail']
        blog.save()
        messages.success(request, "✨ Blog successfully updated!")
        return redirect('edit_blog', blog_id=blog.id)

    return render(request, 'edit_blog.html', {'blog': blog, 'categories': categories})


def edit_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    categories = Category.objects.all()

    if request.method == "POST":
        video.title = request.POST.get('title')
        video.description = request.POST.get('description')
        video.video_url = request.POST.get('video_url')
        video.category_id = request.POST.get('category') or None
        if 'thumbnail' in request.FILES:
            video.thumbnail = request.FILES['thumbnail']
        video.save()
        messages.success(request, "✨ Video successfully updated!")
        return redirect('edit_video', video_id=video.id)

    return render(request, 'edit_video.html', {'video': video, 'categories': categories})


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    categories = Category.objects.all()
    chapters = course.chapters.all().order_by('order')
    final_tests = course.final_tests.all()

    if request.method == "POST":
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.price = request.POST.get('price')
        course.category_id = request.POST.get('category') or None

        if 'material' in request.FILES:
            course.material = request.FILES['material']
        if 'thumbnail' in request.FILES:
            course.thumbnail = request.FILES['thumbnail']
        course.save()

        # 🧱 Clear old data
        CourseChapter.objects.filter(course=course).delete()
        FinalTest.objects.filter(course=course).delete()

        # 🔁 Chapters
        chapter_titles = request.POST.getlist('chapter_title[]')
        chapter_contents = request.POST.getlist('chapter_content[]')
        chapter_videos = request.POST.getlist('chapter_video[]')
        quiz_questions = request.POST.getlist('quiz_question[]')
        quiz_option_a = request.POST.getlist('quiz_option_a[]')
        quiz_option_b = request.POST.getlist('quiz_option_b[]')
        quiz_option_c = request.POST.getlist('quiz_option_c[]')
        quiz_option_d = request.POST.getlist('quiz_option_d[]')
        quiz_correct = request.POST.getlist('quiz_correct[]')

        quiz_index = 0
        for i in range(len(chapter_titles)):
            chapter = CourseChapter.objects.create(
                course=course,
                title=chapter_titles[i],
                content=chapter_contents[i],
                video_url=chapter_videos[i],
                order=i+1
            )

            if quiz_index < len(quiz_questions):
                ChapterQuiz.objects.create(
                    chapter=chapter,
                    question=quiz_questions[quiz_index],
                    option_a=quiz_option_a[quiz_index],
                    option_b=quiz_option_b[quiz_index],
                    option_c=quiz_option_c[quiz_index],
                    option_d=quiz_option_d[quiz_index],
                    correct_answer=quiz_correct[quiz_index]
                )
                quiz_index += 1
        # Determine the number of valid chapters (based on the minimum length of inputs)
        chapter_count = min(len(chapter_titles), len(chapter_contents), len(chapter_videos))

        for i in range(chapter_count):
            chapter = CourseChapter.objects.create(
                course=course,
                title=chapter_titles[i],
                content=chapter_contents[i],
                video_url=chapter_videos[i],
                order=i + 1
            )

        # Optional: Check if quiz data exists for the chapter
        if quiz_index < len(quiz_questions):
            ChapterQuiz.objects.create(
                chapter=chapter,
                question=quiz_questions[quiz_index],
                option_a=quiz_option_a[quiz_index],
                option_b=quiz_option_b[quiz_index],
                option_c=quiz_option_c[quiz_index],
                option_d=quiz_option_d[quiz_index],
                correct_answer=quiz_correct[quiz_index]
            )
            quiz_index += 1


        # ✅ Final Test
        final_q = request.POST.getlist('final_question[]')
        final_a = request.POST.getlist('final_option_a[]')
        final_b = request.POST.getlist('final_option_b[]')
        final_c = request.POST.getlist('final_option_c[]')
        final_d = request.POST.getlist('final_option_d[]')
        final_correct = request.POST.getlist('final_correct[]')

        for i in range(len(final_q)):
            FinalTest.objects.create(
                course=course,
                question=final_q[i],
                option_a=final_a[i],
                option_b=final_b[i],
                option_c=final_c[i],
                option_d=final_d[i],
                correct_answer=final_correct[i]
            )

        messages.success(request, "✅ Course and content updated successfully.")
        return redirect('edit_course', course_id=course.id)

    return render(request, 'edit_course.html', {
        'course': course,
        'categories': categories,
        'chapters': chapters,
        'final_tests': final_tests,
    })


def edit_webinar(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    categories = Category.objects.all()


    if request.method == "POST":
        webinar.title = request.POST.get('title')
        webinar.description = request.POST.get('description')
        webinar.date = request.POST.get('date')
        webinar.price = request.POST.get('price')
        webinar.link = request.POST.get('link')
        webinar.access_code = request.POST.get('access_code')
        if 'thumbnail' in request.FILES:
            webinar.thumbnail = request.FILES['thumbnail']
        webinar.save()
        messages.success(request, "✨ Webinar successfully updated!")
        return redirect('edit_webinar', webinar_id=webinar.id)

    return render(request, 'edit_webinar.html', {'webinar': webinar,'categories': categories,})



from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import BlogPost, Category

def blog_list(request):
    category_id = request.GET.get('category')
    page = request.GET.get('page', 1)
    
    blogs = BlogPost.objects.all().order_by('-created_at')
    
    if category_id:
        blogs = blogs.filter(category_id=category_id)

    paginator = Paginator(blogs, 4)  # 4 per page
    page_obj = paginator.get_page(page)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/_blog_list.html', {'page_obj': page_obj})


    categories = Category.objects.all()
    return render(request, 'blog_list.html', {'page_obj': page_obj, 'categories': categories})



from .models import BlogPost

def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.views += 1
    post.save()
    return render(request, 'blog_detail.html', {'post': post})


from .models import Course, Webinar
def signup(request):
    return render(request, 'account/signup.html')


def signin(request):
    return render(request, 'account/signin.html')
    
from django.contrib.auth.decorators import login_required
from .models import Webinar, Course, Video, Payment

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Webinar, Course, Payment

from django.utils import timezone
from django.db.models import Q



@login_required
def webinar(request):
    filter_type = request.GET.get('filter')
    show_all = request.GET.get('show_all')

    if filter_type == 'past':
        webinars = Webinar.objects.filter(date__lt=timezone.now()).order_by('-date')
    elif filter_type == 'free':
        webinars = Webinar.objects.filter(price=0).order_by('-date')
    elif filter_type == 'premium':
        webinars = Webinar.objects.filter(price__gt=0).order_by('-date')
    else:
        # Default: show the most recent webinars (past or upcoming)
        webinars = Webinar.objects.all().order_by('-date')

    # Show only 6 if show_all is not set
    if not show_all:
        webinars = webinars[:6]

    # Fetch paid items
    if request.user.is_authenticated:
        paid_courses = list(Payment.objects.filter(
            user=request.user,
            payment_type__iexact="course",
            status__iexact="Completed"
        ).values_list('item_id', flat=True))

        paid_webinars = list(Payment.objects.filter(
            user=request.user,
            payment_type__iexact="webinar",
            status__iexact="Completed"
        ).values_list('item_id', flat=True))

        # Convert to integers
        paid_webinars = [int(id) for id in paid_webinars]

    else:
        paid_courses = []
        paid_webinars = []

    # Get the next upcoming webinar for countdown
    next_webinar = Webinar.objects.filter(date__gt=timezone.now()).order_by('date').first()

    return render(request, 'webinar.html', {
        'webinars': webinars,
        'selected_filter': filter_type,
        'next_webinar': next_webinar,
        'show_all': show_all,
        'paid_courses': paid_courses,
        'paid_webinars': paid_webinars,
    })


from django.db.models import Q
from .models import Course, Payment, Category

@login_required
def courses(request):
    query = request.GET.get('q', '')
    selected_category = request.GET.get('category', '')
    show_all = request.GET.get('show_all', '')

    courses = Course.objects.select_related('category').all().order_by('-id')

    if not show_all and not query and not selected_category:
        courses = courses[:6]  # Show latest 10 by default

    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if selected_category:
        courses = courses.filter(category__name=selected_category)

    if request.user.is_authenticated:
        paid_courses = list(Payment.objects.filter(
        user=request.user,
            payment_type__iexact="course",
            status__iexact="Completed"  # case-insensitive
        ).values_list('item_id', flat=True))

        paid_webinars = list(Payment.objects.filter(
            user=request.user,
            payment_type__iexact="webinar",
            status__iexact="Completed"
        ).values_list('item_id', flat=True))


    else:
        paid_courses = []
        paid_webinars = []

    # All unique course categories
    categories = Category.objects.filter(course__isnull=False).distinct()

    return render(request, 'courses.html', {
        'courses': courses,
        'query': query,
        'selected_category': selected_category,
        'categories': categories,
        'showing_all': bool(show_all or query or selected_category),
        'paid_courses': paid_courses,
        'paid_webinars': paid_webinars,
    })

from django.db.models import Q
from .models import Video, Category

def videos(request):
    query = request.GET.get("q", "")
    selected_category = request.GET.get("category", "")

    videos = Video.objects.select_related('category').all().order_by('-id')

    if query:
        videos = videos.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if selected_category:
        videos = videos.filter(category__name=selected_category)

    # ✅ Limit to last 6 after filtering
    videos = videos[:6]

    categories = Category.objects.filter(video__isnull=False).distinct()

    return render(request, 'videos.html', {
        'videos': videos,
        'query': query,
        'selected_category': selected_category,
        'categories': categories
    })


def donation(request):
    return render(request, 'donation.html')
# views.py





from .models import BlogPost, Video, Course, Webinar, Category
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages

from django.db.models import Count, Sum
from .models import Video, BlogPost, Course, Webinar, Payment, ChapterQuiz, FinalTest, CourseChapter, CourseCompletion


from django.contrib.auth import get_user_model
User = get_user_model()
@login_required


def dashboard(request):
    videos = Video.objects.all()
    blogs = BlogPost.objects.all()
    courses = Course.objects.all()
    webinars = Webinar.objects.all()
    users = User.objects.all()
    recent_payments = Payment.objects.all().order_by('-date')[:5]
    categories = Category.objects.all()

    if request.method == 'POST':
        # Upload Video
        if 'upload_video' in request.POST:
            title = request.POST.get('video_title')
            category = request.POST.get('video_category')
            video_url = request.POST.get('video_url')
            thumbnail = request.FILES.get('video_thumbnail')

            if not title or not category or not video_url or not thumbnail:
                messages.error(request, "All video fields are required.")
            else:
                Video.objects.create(
                    title=title,
                    category_id=category,
                    video_url=video_url,
                    thumbnail=thumbnail
                )
                messages.success(request, "Video uploaded successfully!")

        # Upload Blog
        elif 'upload_blog' in request.POST:
            title = request.POST.get('blog_title')
            category = request.POST.get('blog_category')
            content = request.POST.get('blog_content')
            thumbnail = request.FILES.get('blog_thumbnail')

            if not title or not category or not content or not thumbnail:
                messages.error(request, "All blog fields are required.")
            else:
                BlogPost.objects.create(
                    title=title,
                    category_id=category,
                    content=content,
                    thumbnail=thumbnail
                )
                messages.success(request, "Blog post published successfully!")

        # Upload Course + Chapters
        elif 'upload_course' in request.POST:
            title = request.POST.get('course_title')
            description = request.POST.get('course_description')
            price = request.POST.get('course_price')
            material = request.FILES.get('course_material')
            thumbnail = request.FILES.get('course_thumbnail')
            category_id = request.POST.get('course_category')

            if not title or not description or not price:
                messages.error(request, "All course fields are required.")
            else:
                course = Course.objects.create(
                    title=title,
                    description=description,
                    price=price,
                    material=material,
                    thumbnail=thumbnail,
                    category_id=category_id if category_id else None
                )

                # Save chapters
                chapter_titles = request.POST.getlist('chapter_title[]')
                chapter_contents = request.POST.getlist('chapter_content[]')
                chapter_videos = request.POST.getlist('chapter_video[]')

                quiz_questions = request.POST.getlist('quiz_question[]')
                quiz_option_a = request.POST.getlist('quiz_option_a[]')
                quiz_option_b = request.POST.getlist('quiz_option_b[]')
                quiz_option_c = request.POST.getlist('quiz_option_c[]')
                quiz_option_d = request.POST.getlist('quiz_option_d[]')
                quiz_correct = request.POST.getlist('quiz_correct[]')

                quiz_index = 0

                for i in range(len(chapter_titles)):
                    if chapter_titles[i] and chapter_contents[i]:
                        chapter = CourseChapter.objects.create(
                            course=course,
                            title=chapter_titles[i],
                            content=chapter_contents[i],
                            video_url=chapter_videos[i],
                            order=i + 1
                        )

                        if quiz_index < len(quiz_questions):
                            ChapterQuiz.objects.create(
                                chapter=chapter,
                                question=quiz_questions[quiz_index],
                                option_a=quiz_option_a[quiz_index],
                                option_b=quiz_option_b[quiz_index],
                                option_c=quiz_option_c[quiz_index],
                                option_d=quiz_option_d[quiz_index],
                                correct_answer=quiz_correct[quiz_index]
                            )
                            quiz_index += 1

                final_questions = request.POST.getlist('final_question[]')
                final_a = request.POST.getlist('final_option_a[]')
                final_b = request.POST.getlist('final_option_b[]')
                final_c = request.POST.getlist('final_option_c[]')
                final_d = request.POST.getlist('final_option_d[]')
                final_correct = request.POST.getlist('final_correct[]')

                for i in range(len(final_questions)):
                    if final_questions[i]:
                        FinalTest.objects.create(
                            course=course,
                            question=final_questions[i],
                            option_a=final_a[i],
                            option_b=final_b[i],
                            option_c=final_c[i],
                            option_d=final_d[i],
                            correct_answer=final_correct[i]
                        )

                messages.success(request, "✅ Course with material, category, thumbnail, chapters, quizzes and final test saved.")

     

        # Upload Webinar
        elif 'upload_webinar' in request.POST:
            title = request.POST.get('webinar_title')
            description = request.POST.get('webinar_description')
            date = request.POST.get('webinar_date')
            price = request.POST.get('webinar_price')
            link = request.POST.get('webinar_link')

            if not title or not description or not date or not price or not link:
                messages.error(request, "All webinar fields are required.")
            else:
                Webinar.objects.create(
                    title=title,
                    description=description,
                    date=date,
                    price=price,
                    link=link
                )
                messages.success(request, "Webinar scheduled successfully!")

    # Top viewed content
    top_videos = Video.objects.order_by('-views')[:5]
    top_blog_posts = BlogPost.objects.order_by('-views')[:5]

    context = {
        'videos': videos,
        'blogs': blogs,
        'courses': courses,
        'webinars': webinars,
        'users': users,
        'recent_payments': recent_payments,
        'categories': categories,
        'top_videos': top_videos,
        'top_blog_posts': top_blog_posts,
    }

    return render(request, 'dashboard.html', context)



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from .models import Course, FinalTest, Payment, CourseCompletion
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
import os

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Course, FinalTest, Payment, CourseCompletion, CourseChapter, ChapterQuiz, ChapterQuizAttempt

@login_required
def final_test_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    tests = FinalTest.objects.filter(course=course)

    has_paid = Payment.objects.filter(
        user=request.user,
        item_id=course.id,
        payment_type='course',
        status='Completed'
    ).exists()

    if not has_paid:
        return HttpResponseForbidden("You must purchase the course first.")

    # Check if already completed
    existing_completion = CourseCompletion.objects.filter(user=request.user, course=course).first()
    if existing_completion:
        return render(request, 'final_test.html', {
            'course': course,
            'tests': tests,
            'score': existing_completion.score,
            'completed': True,
        })

    if request.method == "POST":
        score = 0
        total = tests.count()
        user_answers = {}

        for test in tests:
            user_answer = request.POST.get(f'question_{test.id}')
            user_answers[test.id] = user_answer
            if user_answer == test.correct_answer:
                score += 1

        percent = round((score / total) * 100, 2)

        CourseCompletion.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={'score': percent, 'completed_at': timezone.now()}
        )

        return render(request, 'final_test.html', {
            'course': course,
            'tests': tests,
            'score': percent,
            'user_answers': user_answers,
            'completed': True,
        })

    return render(request, 'final_test.html', {'course': course, 'tests': tests})


@login_required
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    completion = CourseCompletion.objects.filter(user=request.user, course=course).first()

    if not completion:
        return HttpResponseForbidden("Complete the course to download your certificate.")

    html_string = render_to_string('certificate_template.html', {
        'user': request.user,
        'course': course,
        'score': completion.score,
        'completed_at': completion.completed_at
    })

    html = HTML(string=html_string)
    fd, path = tempfile.mkstemp()
    try:
        os.close(fd)
        html.write_pdf(target=path)
        with open(path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'
            return response
    finally:
        os.remove(path)


import csv
from .models import Payment  # or whichever model you're exporting

def download_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Amount', 'Type', 'Status', 'Date'])

    for payment in Payment.objects.all():
        writer.writerow([
            payment.user.username,
            payment.amount,
            payment.payment_type,
            payment.status,
            payment.date,
        ])

    return response


from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Webinar
from django.conf import settings



from .models import Course, Webinar, PaymentMethod

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    payment_methods = PaymentMethod.objects.all()
    return render(request, 'course_detail.html', {
        'item': course,
        'item_type': 'course',
        'payment_methods': payment_methods
    })



from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Course, Webinar, Payment


@login_required
def course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    is_paid = Payment.objects.filter(
        user=request.user,
        item_id=course.id,
        payment_type__iexact="course",
        status__iexact="Completed"
    ).exists()

    if not is_paid:
        return HttpResponseForbidden("Access Denied. You have not purchased this course.")

    chapters = course.chapters.all().order_by('order')
    final_test = course.final_tests.all()

    course_completion = CourseCompletion.objects.filter(user=request.user, course=course).first()
    is_completed = course_completion is not None

    attempts = ChapterQuizAttempt.objects.filter(user=request.user, chapter__in=chapters)
    attempt_dict = {a.chapter.id: a for a in attempts}

    unlocked_chapters = []
    passed = True  # allow first chapter
    for chapter in chapters:
        if passed:
            unlocked_chapters.append(chapter)
        passed = chapter.id in attempt_dict and attempt_dict[chapter.id].score >= 60  # require 60% to unlock

    return render(request, 'course_view.html', {
        'course': course,
        'chapters': unlocked_chapters,
        'final_test': course.final_tests.all(),
        'quiz_attempts': attempt_dict,
        'is_completed': is_completed,
        'final_score': course_completion.score if course_completion else None
    })


from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .models import ChapterQuiz, ChapterQuizAttempt

@require_POST
@login_required
def submit_chapter_quiz(request, chapter_id):
    chapter = get_object_or_404(CourseChapter, id=chapter_id)
    quizzes = chapter.quizzes.all()
    total = quizzes.count()
    score = 0

    for quiz in quizzes:
        selected = request.POST.get(f"quiz_{quiz.id}")
        if selected and selected == quiz.correct_answer:
            score += 1

    percent = (score / total) * 100

    ChapterQuizAttempt.objects.update_or_create(
        user=request.user,
        chapter=chapter,
        defaults={'score': percent}
    )

    messages.success(request, f"You scored {percent:.2f}% on this quiz.")
    return redirect('course_view', course_id=chapter.course.id)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Webinar, Payment

@login_required
def webinar_view(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)

    is_paid = Payment.objects.filter(
        user=request.user,
        item_id=webinar.id,
        payment_type__iexact="webinar",
        status__iexact="Completed"
    ).exists()

    if not is_paid:
        return HttpResponseForbidden("Access Denied. You have not purchased this webinar.")

    access_code = str(webinar.id + 1000)

    return render(request, 'webinar_view.html', {
        'webinar': webinar,
        'access_code': access_code
    })




from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Webinar, PaymentMethod, Payment
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Webinar, PaymentMethod  # adjust imports as needed
import stripe
import midtransclient
from midtransclient import Snap

snap = midtransclient.Snap(
    is_production=settings.MIDTRANS_IS_PRODUCTION,
    server_key=settings.MIDTRANS_SERVER_KEY,  # ✅ server key
    client_key=settings.MIDTRANS_CLIENT_KEY   # ✅ client key
)


stripe.api_key = settings.STRIPE_SECRET_KEY
MIDTRANS_CLIENT_KEY: settings.MIDTRANS_CLIENT_KEY

def webinar_detail(request, pk):
    webinar = get_object_or_404(Webinar, pk=pk)
    payment_methods = PaymentMethod.objects.all()
    
    return render(request, 'webinar_detail.html', {
        'webinar': webinar,                 # ✅ Added this line
        'item': webinar,
        'item_type': 'webinar',
        'payment_methods': payment_methods,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    })

@login_required
def start_payment(request):
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        amount = request.POST.get('amount')
        name = request.POST.get('name')
        email = request.POST.get('email')
        payment_method_id = request.POST.get('payment_method')

        item_model = Course if item_type == 'course' else Webinar
        item = get_object_or_404(item_model, id=item_id)

        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)

        # 💳 Create Payment
        Payment.objects.create(
            user=request.user,
            amount=amount,
            payment_type=item_type,
            item_id=item_id,
            payment_method=payment_method,
            status='Completed',
        )

        return redirect('payment_success', item_type=item_type, item_id=item.id)

    return redirect('home')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest

@login_required
@csrf_exempt
def create_stripe_checkout_session(request):
    try:
        if request.method == 'POST':
            item_type = request.POST.get('item_type')
            item_id = request.POST.get('item_id')
            name = request.POST.get('name')
            email = request.POST.get('email')

            item_model = Course if item_type == 'course' else Webinar
            item = get_object_or_404(item_model, id=item_id)

            session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'idr',
                    'product_data': {
                        'name': item.title,
                        'description': item.description,
                    },
                    'unit_amount': int(item.price * 100),  # MUST be integer
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email=email,
            success_url=request.build_absolute_uri(
                f"/payment_success/{item_type}/{item.id}/"
            ),
            cancel_url=request.build_absolute_uri('/payment/cancelled/'),
        )
            return JsonResponse({'id': session.id})

        return HttpResponseBadRequest("Only POST allowed")
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

import midtransclient
import uuid

import midtransclient
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
@csrf_exempt
def get_snap_token(request):
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        item_model = Course if item_type == 'course' else Webinar
        item = get_object_or_404(item_model, id=item_id)

        snap = midtransclient.Snap(
            is_production=settings.MIDTRANS_IS_PRODUCTION,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )

        order_id = f'ORDER-{uuid.uuid4()}'
        transaction = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": int(item.price),
            },
            "customer_details": {
                "first_name": request.user.first_name or request.user.username,
                "email": request.user.email,
            }
        }

        try:
            snap_token = snap.create_transaction(transaction)['token']
            return JsonResponse({'snap_token': snap_token})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def payment_success(request, item_type, item_id):
    item = None
    template_data = {}

    if item_type == "course":
        item = get_object_or_404(Course, id=item_id)
        template_data = {
            'item_type': 'course',
            'title': item.title,
            'material': item.material.url,  # assuming FileField
        }

    elif item_type == "webinar":
        item = get_object_or_404(Webinar, id=item_id)
        access_code = item.id + 1000  # or use any logic you like
        template_data = {
            'item_type': 'webinar',
            'title': item.title,
            'link': item.link,  # 💡 Admin-provided Zoom link
            'access_code': access_code,
            'webinar_id': item.id,
        }
    # Add this in payment_success before returning the template
    if not Payment.objects.filter(user=request.user, item_id=item_id, payment_type=item_type, payment_method__name='Stripe').exists():
        stripe_method = PaymentMethod.objects.get_or_create(name='Stripe')[0]
        amount = item.price
        Payment.objects.create(
            user=request.user,
            amount=amount,
            payment_type=item_type,
            item_id=item.id,
            payment_method=stripe_method,
            status='Completed',
        )

    return render(request, 'payment_success.html', template_data)



from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
import tempfile
import os

def download_ticket(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    access_code = webinar.id + 1000  # or your logic

    html_string = render_to_string('ticket_template.html', {
        'webinar': webinar,
        'access_code': access_code,
    })

    html = HTML(string=html_string)

    # Use mkstemp instead of NamedTemporaryFile
    fd, path = tempfile.mkstemp()
    try:
        os.close(fd)  # Close the file descriptor immediately
        html.write_pdf(target=path)

        with open(path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Webinar_Ticket.pdf"'
            return response
    finally:
        os.remove(path)  # Clean up the temporary file



from .models import Course, Webinar, Payment, PaymentMethod
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

@login_required
def checkout(request, item_type, pk):
    item = None
    if item_type == "course":
        item = get_object_or_404(Course, pk=pk)
    elif item_type == "webinar":
        item = get_object_or_404(Webinar, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        payment_method_id = request.POST.get('payment_method')

        if item.price == 0:
            # Free content, register without payment
            return render(request, 'thank_you.html', {'name': name, 'item': item})

        payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id)
        
        # Save payment record (status pending for now)
        # views.py inside checkout()

        Payment.objects.create(
            user=request.user,
            amount=item.price,
            payment_type=item_type,
            item_id=item.id,  # NEW: link payment to item
            status='Pending',
            payment_method=payment_method,
            date=timezone.now()
        )


        return render(request, 'thank_you.html', {
            'name': name,
            'item': item,
            'payment_method': payment_method
        })

    payment_methods = PaymentMethod.objects.all()
    return render(request, 'checkout.html', {
        'item': item,
        'item_type': item_type,
        'payment_methods': payment_methods
    })

