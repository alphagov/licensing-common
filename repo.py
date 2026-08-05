# import django
# import os
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "common.settings")
#
# django.setup()
#
# # from common.models.licences import Licence
#
#
#
#
# if __name__ == "__main__":
#     licence = Licence.objects.get(pk='50c8520393867870cb0d76d6')
#     print("\nLicence ======>", licence.__dict__)
#     print("\n   ADMIN AREA ======>:", licence.administrative_area.__dict__)
#     for interaction in licence.licence_interactions:
#         print("\n   INTERACTION =====>", interaction.__dict__)
#         print("\n       FORM =====>", interaction.form.__dict__)
#         for doc in interaction.supporting_documents:
#             print("\n           SUPPORTING DOCS =====>", doc.__dict__)
#
#         print("\n       FEE ====>", interaction.fee.__dict__)
#
#     count=0
#     for char in "application-to-register-as-a-childrens-social-care-provider-independent-fostering-service":
#         count+=1
#     print("\n   COUNT ====>", count)
