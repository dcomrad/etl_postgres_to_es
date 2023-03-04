import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), null=True, blank=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('name'), max_length=255)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _('person')
        verbose_name_plural = _('people')

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), null=True, blank=True)
    creation_date = models.DateTimeField(_('creation_date'), auto_now_add=True,
                                         null=True)
    file_path = models.FileField(_('file'), blank=True, null=True,
                                 upload_to='movies/')
    rating = models.FloatField(_('rating'), null=True, blank=True, default=0,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])
    type = models.TextField(
        choices=[('movie', _('movie')), ('tv_show', _('tv_show'))],
        null=True, verbose_name=_('type')
    )
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _('filmwork')
        verbose_name_plural = _('filmworks')

        indexes = [
            models.Index(name='film_work_creation_date_idx',
                         fields=['creation_date']),
        ]

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(to=Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(to=Genre, on_delete=models.CASCADE)
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'

        indexes = [
            models.Index(name='film_work_genre_idx',
                         fields=['film_work_id', 'genre_id']),
        ]

        constraints = [
            models.UniqueConstraint(
                name='film_work_genre_unique',
                fields=['film_work_id', 'genre_id']
            )
        ]


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(to=Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(to=Person, on_delete=models.CASCADE)
    role = models.TextField(
        choices=[('actor', _('actor')),
                 ('director', _('director')),
                 ('writer', _('writer'))],
        null=True, verbose_name=_('role')
    )
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'

        indexes = [
            models.Index(name='film_work_person_idx',
                         fields=['film_work_id', 'person_id', 'role']),
        ]
