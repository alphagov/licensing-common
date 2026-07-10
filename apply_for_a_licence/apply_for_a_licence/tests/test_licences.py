from apply_for_a_licence.enums.countries import Countries
from apply_for_a_licence.models.licences import AdministrativeArea


def test_valid_admin_area():
    admin_area = AdministrativeArea(
        code="7",
        countries=[Countries.NORTHERN_IRELAND.value, Countries.ENGLAND.value],
    )
    print(admin_area.__dict__)

    admin_area.full_clean()
    assert admin_area.name == "NI,England"