from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("blog_list", views.blog_list, name="blog_list"),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('webinar/<int:pk>/', views.webinar_detail, name='webinar_detail'),
    path("videos", views.videos, name="videos"),
    path("webinar", views.webinar, name="webinar"),
    path("courses", views.courses, name="courses"),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('webinar/<int:pk>/', views.webinar_detail, name='webinar_detail'),
    path('course/view/<int:course_id>/', views.course_view, name='course_view'),
    path('chapter/<int:chapter_id>/quiz/', views.submit_chapter_quiz, name='submit_chapter_quiz'),
    path('webinar/view/<int:webinar_id>/', views.webinar_view, name='webinar_view'),
    path('start_payment/', views.start_payment, name='start_payment'),
    path('create-checkout-session/', views.create_stripe_checkout_session, name='create_stripe_checkout_session'),
    path('payment/snap-token/', views.get_snap_token, name='get_snap_token'),
    path('payment_success/<str:item_type>/<int:item_id>/', views.payment_success, name='payment_success'),
    path('checkout/<str:item_type>/<int:pk>/', views.checkout, name='checkout'),
    path("dashboard", views.dashboard, name="dashboard"),
    path("donation", views.donation, name="donation"),
    path('download-csv/', views.download_csv, name='download_csv'),

    path('download-ticket/<int:webinar_id>/', views.download_ticket, name='download_ticket'),
    path('edit/blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('edit/video/<int:video_id>/', views.edit_video, name='edit_video'),
    path('edit/webinar/<int:webinar_id>/', views.edit_webinar, name='edit_webinar'),
    path('edit/course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course/<int:course_id>/final-test/', views.final_test_view, name='final_test_view'),
    path('course/<int:course_id>/certificate/', views.download_certificate, name='download_certificate'),
    
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='account_logout'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)