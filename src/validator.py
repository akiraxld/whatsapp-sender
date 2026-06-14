import re


def clean_phone(raw: str) -> str:
    # убираем скобки, дефисы, пробелы
    return re.sub(r'[\s\(\)\-]', '', str(raw))


def validate_phone(raw, row_index: int) -> tuple[str | None, str | None]:
    """
    Возвращает (очищенный номер, None) если всё ок,
    или (None, описание ошибки) если номер невалидный.
    """

    # кейс: пустая строка / NaN
    if not raw or str(raw).strip() in ('', 'nan'):
        return None, f"[ERROR] Строка {row_index}: Номер телефона отсутствует"

    phone = clean_phone(raw)

    # кейс: вместо номера текст
    digits_only = phone.lstrip('+')
    if not digits_only.isdigit():
        return None, f"[ERROR] Строка {row_index}: Номер '{raw}' содержит недопустимые символы"

    # кейс: номер начинается с 8 и длина 11 — заменяем на +7
    if phone.startswith('8') and len(phone) == 11:
        phone = '+7' + phone[1:]

    # кейс: номер без + но начинается с 7 и длина 11
    if phone.startswith('7') and not phone.startswith('+') and len(phone) == 11:
        phone = '+' + phone

    # кейс: короткий или длинный номер (казахстан = +7 + 10 цифр = 12 символов)
    if len(phone) != 12:
        return None, f"[ERROR] Строка {row_index}: Номер '{raw}' имеет неверную длину ({len(phone)} символов, ожидается 12)"

    return phone, None
