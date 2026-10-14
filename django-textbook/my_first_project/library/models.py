from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    class Meta:
        ordering = ['last_name', 'first_name']


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    established = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class BookManager(models.Manager):
    def available(self):
        return self.get_queryset().filter(is_available=True)

    def high_rated(self, threshold=4):
        return self.get_queryset().filter(rating__gte=threshold)

class Book(models.Model):
    GENRE_CHOICES = [
        ('F', 'Fiction'), ('NF', 'Non-Fiction'), ('SF', 'Science Fiction'),
        ('FAN', 'Fantasy'), ('MYS', 'Mystery'), ('THR', 'Thriller'),
        ('ROM', 'Romance'), ('HIS', 'Historical'), ('BIO', 'Biography'),
        ('SCI', 'Science'), ('TEC', 'Technology'),
    ]

    title = models.CharField(max_length=200, help_text="The book's full title")
    subtitle = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, unique=True,
                             help_text="The book's unique 13-digit ISBN")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    co_authors = models.ManyToManyField(Author, related_name='co_authored_books', blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='books')
    publication_date = models.DateField()
    genre = models.CharField(max_length=3, choices=GENRE_CHOICES, default='F')
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    summary = models.TextField(help_text="Brief description of the book")
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    is_available = models.BooleanField(default=True)
    borrowed_count = models.IntegerField(default=0)
    rating = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BookManager()

    def __str__(self):
        return self.title

    def full_title(self):
        if self.subtitle:
            return f"{self.title}: {self.subtitle}"
        return self.title
    def can_be_borrowed(self):
        return self.is_available

    @property
    def age(self):
        return (timezone.now().date() - self.publication_date).days // 365
    def is_recent(self):
        return (timezone.now().date() - self.publication_date).days < 1825

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['genre']),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(pages__gte=1), name='pages_positive'),
            models.UniqueConstraint(fields=['title', 'author'], name='unique_title_author'),
        ]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"