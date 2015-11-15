from django.conf import settings
from django.db import models
from website.utils import Address, GeoRangeChecker
from django.core.mail import send_mass_mail


class Group(models.Model):
    PUBLIC = "public"
    PRIVATE = "private"
    SECRET = "secret"
    SEARCHABLE_TYPES = [
        PUBLIC,
        PRIVATE
    ]
    PRIVACY_CHOICES = (
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (SECRET, 'Secret'),
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="admin"
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
    )
    name = models.CharField(max_length=64,unique=True)
    type = models.CharField(
        max_length=7,
        choices=PRIVACY_CHOICES,
        default=PUBLIC
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/group/%i/" % self.id


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=64)
    groups = models.ManyToManyField(Group)
    address = models.CharField(max_length=64)
    city = models.CharField(max_length=254)
    state = models.CharField(max_length=64)
    zipcode = models.CharField(max_length=64)
    date = models.DateField()
    time = models.TimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.title

    def get_formatted_address(self):
        return str(Address(self.address, self.city, self.state, self.zipcode))

    def notify(self):
        users_to_notify = []
        for group in self.groups.all():
            for user in group.users.all():
                for notification_zone in NotificationZone.objects.filter(user=user):
                    is_in_range = GeoRangeChecker.is_in_range_mi(
                        notification_zone.radius,
                        notification_zone.latitude,
                        notification_zone.longitude,
                        self.latitude,
                        self.longitude
                    )
                    if is_in_range:
                        users_to_notify.append(user)
        messages = []
        for user in users_to_notify:
            body = "Hey! {0} wanted you to know about something happening on {1} at {2}".format(self.user.username, self.date, self.time)
            message = ('KnoWhere: %s' % self.title,
                       body,
                       'notify@knowhere.com',
                       ["%s" % user.email])
            messages.append(message)
        send_mass_mail(messages, fail_silently=False)


class NotificationZone(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL
    )
    groups = models.ManyToManyField(
        Group,
        blank=True
    )
    name = models.CharField(max_length=64)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=64)
    city = models.CharField(max_length=254)
    state = models.CharField(max_length=64)
    zipcode = models.CharField(max_length=64)
    radius = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return self.name