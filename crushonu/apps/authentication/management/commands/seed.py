from django.core.management.base import BaseCommand
from django.db import transaction
from crushonu.apps.authentication.models import User, UserPhoto

from django.core.files import File
from faker import Faker
from datetime import date
from math import sqrt


def is_prime(n):
    if n == 1:
        return False
    elif n == 2:
        return True
    else:
        for x in range(2, int(sqrt(n))+1):
            if n % x == 0:
                return False
        return True


class Command(BaseCommand):
    help = 'Populate database with initial data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        users = list()
        fake = Faker()

        for i in range(1, 31):
            gender = User.MAN
            preference = User.ALL

            if i % 2 == 0:
                gender = User.WOMAN
                preference = User.MAN

            elif is_prime(i):
                gender = User.NEUTRAL
                preference = User.WOMAN

            users.append(
                User(
                    email=f'test{i}@mail.com',
                    birthday=date(1990, 1, 1),
                    gender=gender,
                    preference=preference,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    description=fake.text(100),
                    is_confirmed=True,
                    has_uploaded_photo=True,
                    has_description=True
                )
            )

        User.objects.bulk_create(users)

        mens = 0
        womens = 0
        neutrals = 0

        for i, user in enumerate(User.objects.all(), start=1):
            user.set_password('123456')
            user.save()

            user_photo = UserPhoto(user=user, is_favorite=True)

            if user.gender == User.MAN:
                mens += 1
                file = open(
                    'crushonu/apps/authentication/management/photos/homem/photo-{}.jpg'.format(
                        (mens % 7)+1),
                    'rb'
                )
                image = File(file)
                user_photo.photos.save(
                    'photo-{}.jpg'.format((i % 7)+1), image)
                user_photo.save()

            elif user.gender == User.WOMAN:
                womens += 1
                file = open(
                    'crushonu/apps/authentication/management/photos/mulher/photo-{}.jpg'.format(
                        (womens % 7)+1),
                    'rb'
                )
                image = File(file)
                user_photo.photos.save(
                    'photo-{}.jpg'.format((i % 7)+1), image)
                user_photo.save()
            else:
                neutrals += 1
                choice = 'homem' if neutrals % 2 == 0 else 'mulher'
                file = open(
                    'crushonu/apps/authentication/management/photos/{}/photo-{}.jpg'.format(
                        choice, (i % 7)+1),
                    'rb'
                )

                image = File(file)
                user_photo.photos.save(
                    'photo-{}.jpg'.format((i % 7)+1), image)
                user_photo.save()
