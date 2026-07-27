import bson
from django.db import models
from django_mongodb_backend.fields import ObjectIdField


class Department(models.Model):
    _id = ObjectIdField(primary_key=True, default=bson.ObjectId, auto_created=True, editable=False)
    authority_slug = models.CharField(default="", max_length=255, blank=True, db_column="authoritySlug")
    name = models.CharField(default="", max_length=255, blank=True, db_column="name")
    helpline_phone_number = models.CharField(default="", max_length=255, blank=True, db_column="helpPhone")
    helpline_email_address = models.EmailField(default="", max_length=255, blank=True, db_column="helpEmail")
    address_line_1 = models.CharField(default="", max_length=255, blank=True, db_column="line1")
    address_line_2 = models.CharField(default="", max_length=255, blank=True, db_column="line2")
    address_line_3 = models.CharField(default="", max_length=255, blank=True, db_column="line3")
    address_line_4 = models.CharField(default="", max_length=255, blank=True, db_column="line4")
    postcode = models.CharField(default="", max_length=255, blank=True, db_column="postcode")
    notification_email_address = models.EmailField(
        default="", max_length=255, blank=True, db_column="notificationEmail"
    )
    default_privacy_notice_url = models.CharField(max_length=255, blank=True, db_column="defaultPrivacyNoticeUrl")

    class Meta:
        db_table = "departments"
        managed = False

    def __str__(self):
        return f"{self.name}"
