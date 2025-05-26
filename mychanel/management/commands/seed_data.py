from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from faker import Faker
import random
import os
from django.core.files import File
from mychanel.models import Category, BlogPost, Video, Course, Webinar, Payment, PaymentMethod

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🌱 Starting data seeding...'))

        # Go three levels up from mychanel/management/commands/ to reach personal_chanel/
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        DEFAULT_THUMBNAIL_PATH = os.path.join(BASE_DIR, 'media_seed', 'default.jpg')

        if not os.path.exists(DEFAULT_THUMBNAIL_PATH):
            self.stderr.write(self.style.ERROR(f"❌ Thumbnail image not found at: {DEFAULT_THUMBNAIL_PATH}"))
            return


        # Debugging line to confirm the path
        print(f"✅ Using thumbnail from: {DEFAULT_THUMBNAIL_PATH}")

        users = list(User.objects.all())
        if not users:
            for _ in range(20):
                user = User.objects.create_user(
                    username=fake.user_name(),
                    email=fake.email(),
                    password='password123'
                )
                users.append(user)
            self.stdout.write(self.style.SUCCESS('✅ 20 users created.'))

        categories = ['AI', 'Health Tech', 'VR/AR', 'Robotics', 'Mental Health']
        category_objs = []
        for name in categories:
            cat, _ = Category.objects.get_or_create(name=name)
            category_objs.append(cat)

        payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery']
        payment_method_objs = []
        for method in payment_methods:
            pm, _ = PaymentMethod.objects.get_or_create(name=method, description=f"Payment via {method}")
            payment_method_objs.append(pm)

        # Blog Posts
        for _ in range(10):
            with open(DEFAULT_THUMBNAIL_PATH, 'rb') as image:
                BlogPost.objects.create(
                    title=fake.sentence(),
                    content=fake.paragraph(nb_sentences=10),
                    category=random.choice(category_objs),
                    views=random.randint(0, 500),
                    thumbnail=File(image, name=f"blog_thumb_{random.randint(1,9999)}.jpg")
                )

        # Videos
        video_sources = [
            lambda: f"https://www.youtube.com/watch?v={fake.lexify(text='???????????')}",
            lambda: f"https://www.tiktok.com/@{fake.user_name()}/video/{random.randint(1000000000, 9999999999)}",
            lambda: f"https://www.instagram.com/reel/{fake.lexify(text='???????????')}/"
        ]
        for _ in range(15):
            with open(DEFAULT_THUMBNAIL_PATH, 'rb') as image:
                Video.objects.create(
                    title=fake.sentence(),
                    description=fake.paragraph(),
                    category=random.choice(category_objs),
                    video_url=random.choice(video_sources)(),
                    views=random.randint(0, 1000),
                    thumbnail=File(image, name=f"video_thumb_{random.randint(1000,9999)}.jpg")
                )

        # Courses
        for _ in range(10):
            with open(DEFAULT_THUMBNAIL_PATH, 'rb') as img:
                Course.objects.create(
                    title=fake.sentence(),
                    description=fake.text(),
                    price=round(random.uniform(10, 100), 2),
                    thumbnail=File(img, name=f"course_thumb_{random.randint(1,9999)}.jpg"),
                    material=File(img, name=f"course_material_{random.randint(1,9999)}.pdf")
                )

        # Webinars
        for _ in range(10):
            with open(DEFAULT_THUMBNAIL_PATH, 'rb') as img:
                Webinar.objects.create(
                    title=fake.sentence(),
                    description=fake.text(),
                    date=fake.future_datetime(),
                    price=round(random.uniform(5, 50), 2),
                    thumbnail=File(img, name=f"webinar_thumb_{random.randint(1,9999)}.jpg"),
                    access_code=fake.lexify(text='????-????')
                )

        # Payments
        # Payments
        courses = list(Course.objects.all())
        webinars = list(Webinar.objects.all())

        statuses = ['Pending', 'Completed', 'Failed']
        types = ['Course', 'Webinar', 'Donation']

        for _ in range(20):
            payment_type = random.choice(['Course', 'Webinar', 'Donation'])

            item_id = None

            if payment_type == 'Course' and courses:
                item = random.choice(courses)
                item_id = item.id
            elif payment_type == 'Webinar' and webinars:
                item = random.choice(webinars)
                item_id = item.id
            elif payment_type == 'Donation':
                # For donation, randomly choose a course or a webinar too!
                if random.choice(['Course', 'Webinar']) == 'Course' and courses:
                    item = random.choice(courses)
                    item_id = item.id
                elif webinars:
                    item = random.choice(webinars)
                    item_id = item.id

            if item_id is None:
                continue  # Skip this payment if no course/webinar found

            Payment.objects.create(
                user=random.choice(users),
                amount=round(random.uniform(5.0, 150.0), 2),
                payment_type=payment_type,
                status=random.choice(statuses),
                payment_method=random.choice(payment_method_objs),
                date=timezone.now(),
                item_id=item_id
            )



        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully! 🎉'))
