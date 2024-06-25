import stripe
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

# Create your models here.

stripe.api_key = settings.STRIPE_SECRET_KEY


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    well_1_donor = models.CharField(max_length=255)
    number_of_wells = models.PositiveIntegerField(default=0)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    well_2_donor = models.TextField(null=True, blank=True)
    well_3_donor = models.TextField(null=True, blank=True)
    well_4_donor = models.TextField(null=True, blank=True)
    well_5_donor = models.TextField(null=True, blank=True)
    tip_added = models.BooleanField(default=False)
    comment = models.TextField(default="")
    donor_stripe_id = models.TextField(null=True, blank=True)
    progress = models.TextField(null=True, blank=True)
    images = models.ManyToManyField('Media', related_name='images', blank=True)
    videos = models.ManyToManyField('Media', related_name='videos', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Create Stripe customer if donor_stripe_id is not already set
        if not self.donor_stripe_id:
            stripe_customer = stripe.Customer.create(
                name=self.name,
                email=self.email
            )
            self.donor_stripe_id = stripe_customer['id']
        super(Customer, self).save(*args, **kwargs)


class Media(models.Model):
    file = models.FileField(upload_to='media/', validators=[FileExtensionValidator(['jpg', 'png', 'mp4', 'avi', 'mov', 'mkv', 'wmv'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
