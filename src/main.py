import sys
import os
from reader import read_contacts
from sender import send_dry_run, send_live

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'contacts.csv')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'dry-run'

    if mode not in ('dry-run', 'live'):
        print(f"[ERROR] Неизвестный режим '{mode}'. Используй: dry-run или live")
        sys.exit(1)

    try:
        contacts = read_contacts(DATA_PATH)
    except FileNotFoundError:
        print(f"[ERROR] Файл не найден: {DATA_PATH}")
        sys.exit(1)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    if mode == 'dry-run':
        send_dry_run(contacts)
    elif mode == 'live':
        send_live(contacts)


if __name__ == '__main__':
    main()
