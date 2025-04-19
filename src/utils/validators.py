import phonenumbers
from phonenumbers import PhoneNumberFormat


def validate_and_normalize_phone(phone: str) -> str:
    try:
        parsed = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number")
        return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValueError("Invalid phone number format")
