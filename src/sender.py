import time
import random
from logger import log
from validator import validate_phone


def _random_delay():
    # пауза 10–25 секунд — имитируем живого человека
    delay = random.uniform(10, 25)
    print(f"[WAIT] Пауза {delay:.1f} сек...")
    time.sleep(delay)


def send_dry_run(contacts: list[dict]):
    print("\n=== РЕЖИМ: dry-run (сообщения НЕ отправляются) ===\n")

    for i, row in enumerate(contacts, start=1):
        raw_phone = row.get('phone')
        message = str(row.get('message', '')).strip()

        phone, error = validate_phone(raw_phone, i)

        if error:
            log(str(raw_phone), '', error)
            continue

        if not message:
            log(phone, '', f"[ERROR] Строка {i}: Текст сообщения отсутствует")
            continue

        log(phone, message, '[DRY-RUN] Сообщение было бы отправлено')


def send_live(contacts: list[dict]):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException

    from config import TEST_PHONE

    print("\n=== РЕЖИМ: live (отправка только на тестовый номер) ===\n")

    test_rows = [r for r in contacts if str(r.get('phone', '')).strip() == TEST_PHONE]
    if not test_rows:
        print(f"[ERROR] Тестовый номер {TEST_PHONE} не найден в CSV")
        return

    row = test_rows[0]
    row_index = next(i for i, r in enumerate(contacts, start=1) if str(r.get('phone', '')).strip() == TEST_PHONE)

    raw_phone = row.get('phone')
    message = str(row.get('message', '')).strip()

    phone, error = validate_phone(raw_phone, row_index)
    if error:
        log(str(raw_phone), '', error)
        return

    if not message:
        log(phone, '', f"[ERROR] Строка {row_index}: Текст сообщения отсутствует")
        return

    driver = None
    try:
        driver = webdriver.Chrome()
        driver.get('https://web.whatsapp.com')

        print("[INFO] Отсканируй QR-код в браузере. Ожидание до 60 секунд...")
        # ждём пока загрузится главная страница после сканирования
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="chat-list"]'))
        )
        print("[INFO] WhatsApp Web загружен.")

        _random_delay()

        url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
        driver.get(url)

        try:
            # ждём появления поля ввода
            send_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="conversation-compose-box-input"]'))
            )
        except TimeoutException:
            # поле не появилось — скорее всего номер не зарегистрирован
            log(phone, message, f"[FAILED] Номер {phone} не зарегистрирован в WhatsApp")
            return

        # ищем кнопку отправки
        send_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Send"]'))
        )
        send_btn.click()

        time.sleep(3)  # ждём чтобы сообщение ушло
        log(phone, message, '[SUCCESS] Сообщение отправлено')

    except WebDriverException as e:
        msg = str(e).splitlines()[0]
        if 'net::ERR' in msg or 'ERR_INTERNET_DISCONNECTED' in msg:
            log(phone, message, '[ERROR] Нет интернет-соединения. Ждём 30 секунд...')
            time.sleep(30)
            log(phone, message, '[ERROR] Повторная попытка не выполнена — завершение')
        else:
            readable = msg if msg.strip() else "Selenium не смог взаимодействовать с элементом (возможно, изменился интерфейс WhatsApp Web)"
            log(phone, message, f'[ERROR] Ошибка браузера: {readable}')

    except Exception as e:
        log(phone, message, f'[ERROR] Неожиданная ошибка: {str(e)}')

    finally:
        if driver:
            driver.quit()
