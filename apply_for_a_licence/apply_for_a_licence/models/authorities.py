import bson
from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.fields import ObjectIdField, ArrayField, EmbeddedModelArrayField, EmbeddedModelField
from django_mongodb_backend.models import EmbeddedModel

from apply_for_a_licence.enums.snac_codes import SnacCodes
from apply_for_a_licence.models.utils import validate_countries



def validate_snac_codes(snac_codes: list):
    if not set(snac_codes).issubset(set(SnacCodes.list())):
        raise ValidationError("Snac codes not valid")


class LicenceDetails(EmbeddedModel):
    licence_code = models.CharField(db_column="licenceCode", max_length=255)
    offered_by_authority = models.BooleanField(db_column="offeredByAuthority")
    using_gov_uk = models.BooleanField(db_column="usingGovUk")
    authority_url = models.CharField(db_column="localAuthorityUrl", default="", blank=True)


class ContactDetails(EmbeddedModel):
    line_one = models.CharField(db_column="lineOne", max_length=255, default="", blank=True)
    line_two = models.CharField(db_column="lineTwo", max_length=255, default="", blank=True)
    line_three = models.CharField(db_column="line3", max_length=255, default="", blank=True)
    city = models.CharField(db_column="city", max_length=255, default="", blank=True)
    post_code = models.CharField(db_column="postCode", max_length=255, default="", blank=True)
    phone_number = models.CharField(db_column="phoneNumber", max_length=255, default="", blank=True)
    email = models.EmailField(db_column="emailAddress", blank=True, default="")


class Authority(models.Model):
    _id = ObjectIdField(primary_key=True, default=bson.ObjectId, auto_created=True, editable=False)
    url_slug = models.SlugField(db_column="urlSlug", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    agency_id = models.IntegerField(db_column="agencyId")
    full_name = models.CharField(db_column="fullName", max_length=255)
    authority_url = models.CharField(db_column="authorityUrl", max_length=255, blank=True)
    snac_codes = ArrayField(models.CharField(max_length=255), db_column="snacCodes", default=[], validators=[validate_snac_codes], blank=True)
    countries = ArrayField(models.CharField(max_length=255), db_column="countries", default=[], validators=[validate_countries])
    encoded_image = models.TextField(db_column="imageBase64encoded", blank=True, default="")
    licence_details = EmbeddedModelArrayField(LicenceDetails, default=[], db_column="licenceDetails")
    contact_details = EmbeddedModelField(ContactDetails, db_column="authorityContactDetailsHolder", default=ContactDetails())

    class Meta:
        db_table = "authorities"
        managed = False
