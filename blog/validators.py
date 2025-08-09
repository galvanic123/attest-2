from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date
from dateutil.relativedelta import relativedelta


def validate_password_complexity(value):
    """
    Валидатор для проверки сложности пароля:
    - минимум 8 символов
    - содержит хотя бы одну цифру
    """
    if len(value) < 8:
        raise ValidationError(
            _("Пароль должен содержать минимум 8 символов."), code="password_too_short"
        )
    if not any(char.isdigit() for char in value):
        raise ValidationError(
            _("Пароль должен содержать хотя бы одну цифру."), code="password_no_digits"
        )


def validate_email_domain(value):
    """
    Валидатор для проверки домена email (разрешены только mail.ru и yandex.ru)
    """
    allowed_domains = ["mail.ru", "yandex.ru"]
    domain = value.split("@")[-1] if "@" in value else ""
    if domain not in allowed_domains:
        raise ValidationError(
            _("Разрешены только email с доменами: %(domains)s"),
            code="invalid_email_domain",
            params={"domains": ", ".join(allowed_domains)},
        )


def validate_adult(birth_date):
    """
    Валидатор для проверки, что пользователю есть 18 лет
    """
    if birth_date:
        age = relativedelta(date.today(), birth_date).years
        if age < 18:
            raise ValidationError(
                _("Автор должен быть старше 18 лет."), code="under_age"
            )


def validate_title_no_bad_words(value):
    """
    Валидатор для проверки заголовка на запрещенные слова
    """
    bad_words = ["ерунда", "глупость", "чепуха"]
    for word in bad_words:
        if word in value.lower():
            raise ValidationError(
                _('Заголовок содержит запрещенное слово: "%(word)s"'),
                code="bad_word",
                params={"word": word},
            )
