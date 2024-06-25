from enum import unique
from django.db import models
from accounts.models import User, UserProfile
from datetime import time, date, datetime
from accounts.utils import send_notification
from datetime import time, date, datetime

class Vendor(models.Model):
    """
    Vendor model represents a vendor in the system, associated with a User and UserProfile.
    
    Fields:
        user (OneToOneField): A one-to-one relationship with the User model.
        user_profile (OneToOneField): A one-to-one relationship with the UserProfile model.
        vendor_name (CharField): The name of the vendor.
        vendor_slug (SlugField): A unique slug for the vendor.
        vendor_license (ImageField): An image field for the vendor's license.
        is_approved (BooleanField): Indicates whether the vendor is approved.
        created_at (DateTimeField): The timestamp when the vendor was created.
        modified_at (DateTimeField): The timestamp when the vendor was last modified.
    """
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns the string representation of the vendor, which is the vendor name.
        """
        return self.vendor_name

    def is_open(self):
        """
        Checks if the vendor is currently open based on today's date and current time.
        
        Returns:
            bool: True if the vendor is open, False otherwise.
        """
        # Check current day's opening hours.
        today_date = date.today()
        today = today_date.isoweekday()
        
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        is_open = None
        for i in current_opening_hours:
            # isOpen = False instead of None and if i.from_hour or i.to_hour:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
                if current_time >= start and current_time <= end:
                    is_open = True
                    break
                else:
                    is_open = False
        return is_open

    def save(self, *args, **kwargs):
        """
        Overrides the save method to send a notification email if the vendor's approval status changes.
        """
        if self.pk is not None:
            # Update
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                    'to_email': self.user.email,
                }
                if self.is_approved == True:
                    # Send notification email
                    mail_subject = "Congratulations! Your restaurant has been approved."
                    send_notification(mail_subject, mail_template, context)
                else:
                    # Send notification email
                    mail_subject = "We're sorry! You are not eligible for publishing your food menu on our marketplace."
                    send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)


DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]

class OpeningHour(models.Model):
    """
    OpeningHour model represents the opening hours for a vendor.
    
    Fields:
        vendor (ForeignKey): A foreign key relationship to the Vendor model.
        day (IntegerField): The day of the week (1 for Monday, 7 for Sunday).
        from_hour (CharField): The opening time in 12-hour format.
        to_hour (CharField): The closing time in 12-hour format.
        is_closed (BooleanField): Indicates whether the vendor is closed on this day.
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        """
        Returns the string representation of the opening hour, which is the day of the week.
        """
        return self.get_day_display()
