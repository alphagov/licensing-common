import bson
from django.db import models
from django_mongodb_backend.fields import ObjectIdField, ArrayField, EmbeddedModelArrayField, EmbeddedModelField
from django_mongodb_backend.models import EmbeddedModel


class LicenceDetails(EmbeddedModel):
    licence_code = models.CharField(db_column="licenceCode", max_length=255),
    offered_by_authority = models.BooleanField(db_column="offeredByAuthority")
    using_gov_uk = models.BooleanField(db_column="usingGovUk")
    authority_url = models.CharField(db_column="localAuthorityUrl", default="")


class ContactDetails(EmbeddedModel):
    line_one = models.CharField(db_column="lineOne", max_length=255, default="")
    line_two = models.CharField(db_column="lineTwo", max_length=255, default="")
    line_three = models.CharField(db_column="line3", max_length=255, default="")
    city = models.CharField(db_column="city", max_length=255, default="")
    post_code = models.CharField(db_column="postCode", max_length=255, default="")
    phone_number = models.CharField(db_column="phoneNumber", max_length=255, default="")
    email = models.EmailField(db_column="emailAddress", blank=True, default="")


class Authority(models.Model):
    _id = ObjectIdField(primary_key=True, default=bson.ObjectId, auto_created=True, editable=False)
    url_slug = models.SlugField(db_column="urlSlug", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    agency_id = models.IntegerField(db_column="agencyId")
    full_name = models.CharField(db_column="fullName", max_length=255)
    authority_url = models.CharField(db_column="authorityUrl", max_length=255, blank=True, null=True)
    snac_codes = ArrayField(models.CharField(max_length=255), db_column="snacCodes", default=[])
    countries = ArrayField(models.CharField(max_length=255), db_column="countries", default=[])
    encoded_image = models.TextField(db_column="imageBase64encoded", blank=True, null=True)
    licence_details = EmbeddedModelArrayField(LicenceDetails, null=False, blank=False, default=[], db_column="licenceDetails")
    contact_details = EmbeddedModelField(ContactDetails, null=False, blank=False, db_column="authorityContactDetailsHolder")

    class Meta:
        db_table = "authorities"
        managed = False
