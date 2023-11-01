import re
from string import ascii_lowercase,ascii_uppercase,digits,punctuation

from pydantic import ValidationError




def _password_length_validator(password):
    if len(password) < 8:
        raise ValidationError("Password length is too low. minimum is 8")
def _password_characters_validator(password):
    char_groups = [ascii_uppercase,ascii_lowercase,digits,punctuation]
    condition_dict = {group:False for group in char_groups}
    for char in password:
        for char_group in char_groups:
            if char in char_group:
                condition_dict[char_group] = True
                break
    assert all(condition_dict.values()), (
        "Password must contain at least one lower case, upper case, digit, punctuation"
    )
def password_validator(raw_password:str):
    return _password_length_validator(raw_password) # and _password_characters_validator(raw_password)


def username_validator(username:str):
    assert len(username) >= 5, "Username must be at least 5 characters"
    assert re.fullmatch(r"\w+", username), (
        "Username must contain only letters, digits and unserscore"
    )
