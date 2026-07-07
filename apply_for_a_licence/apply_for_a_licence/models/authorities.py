import bson
from django.db import models
from django_mongodb_backend.fields import ObjectIdField, ArrayField, EmbeddedModelArrayField
from django_mongodb_backend.models import EmbeddedModel


class LicenceDetails(EmbeddedModel):
    licence_code = models.CharField("licenceCode", max_length=255),
    offered_by_authority = models.BooleanField("offeredByAuthority")
    using_gov_uk = models.BooleanField("usingGovUk")
    authority_url = models.CharField("localAuthorityUrl", default="")


class ContactDetails(EmbeddedModel):
    line_one = models.CharField("lineOne", max_length=255, default="")
    line_two = models.CharField("lineTwo", max_length=255, default="")
    line_three = models.CharField("line3", max_length=255, default="")
    city = models.CharField("city", max_length=255, default="")
    post_code = models.CharField("postCode", max_length=255, default="")
    phone_number = models.CharField("phoneNumber", max_length=255, default="")
    email = models.EmailField("emailAddress", blank=True, default="")

class Authority(models.Model):
    _id = ObjectIdField(primary_key=True, default=bson.ObjectId, auto_created=True, editable=False)
    url_slug = models.SlugField("urlSlug", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    full_name = models.CharField("fullName", max_length=255)
    authority_url = models.CharField("authorityUrl", max_length=255, blank=True, null=True)
    snac_codes = ArrayField(models.CharField(max_length=255), verbose_name="snacCodes", default=[])
    countries = ArrayField(models.CharField(max_length=255), verbose_name="countries", default=[])
    encoded_image = models.CharField("imageBase64encoded", blank=True, null=True)
    licence_details = EmbeddedModelArrayField(LicenceDetails, null=False, blank=False, default=[], verbose_name="licenceDetails")
    contact_details = EmbeddedModelArrayField(ContactDetails, null=False, blank=False, default=[], verbose_name="authorityContactDetailsHolder")

    class Meta:
        db_table = "authorities"
        managed = False
