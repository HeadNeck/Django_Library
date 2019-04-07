
from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date


class Genre(models.Model):

    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    # Foreign Key используется потому что книга может иметь только одного автора, а автор несколько книг
    # Автор в виде строки, а не объекта, поскольку он еще не был объявлен в файле.
    # on_delete - обязательное поле(действия при удалении объекта)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")

    # ManyToManyField используется потому что книга может иметь много жанров и наоборот
    # Genre был уже объявлен как класс поэтому объявлен как объект

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Возвращает URL для доступа к конкретному экземпляру книги.
        """
        return reverse('book-detail', args=[str(self.id)])


    def display_genre(self):
        """
        Создает строку для жанра. Это необходимо для отображения жанра в Admin.
        """
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])
    display_genre.short_description = 'Genre' #для отоображения Genre вместо Display Genre



class BookInstance(models.Model):
    """
    Модель, представляющая конкретную копию книги
    (то есть, которая может быть заимствована из библиотеки).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)

    due_back = models.DateField(null=True, blank=True)


    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        #('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='a', help_text='Book availability')

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),
                       ("PermissionRequiredMixin", "Can see borrowed books"),)

    def __str__(self):
        """
        String for representing the Model object
        """
        return '%s (%s)' % (self.id, self.book.title)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    def get_absolute_url(self):
        """
        Возвращает URL для доступа к конкретному экземпляру книги.
        """
        return reverse('book_instance_update', args=[str(self.id)])


class Author(models.Model):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """
        Returns the url to access a particular author instance.
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """
        return '%s, %s' % (self.last_name, self.first_name)

    class Meta:

        ordering = ['last_name']