from schedule import every, run_pending
from logging import getLogger, INFO, warning
from time import sleep
from app.execute import Execute, ExecuteError
from app.external import DatabaseError

logger = getLogger()
logger.setLevel(INFO)

RETRIES = 3

def sleep_time(retry: int) -> int:
    """Rosnący interwał czasu pomiędzy kolejnymi próbami."""
    return (4*(RETRIES - retry) + 1) * 60**2


def execute(retry: int = RETRIES):
    """Wykonaj program, ewentualnie spróbuj ponownie."""
    try:
        return Execute()
    except (DatabaseError, ExecuteError) as error:
        warning(error)
        sleep(sleep_time(retry))
        if retry >= 0:
            execute(retry=retry-1)

def run():
    while True:
        run_pending()
        sleep(3)

every().day.at("00:00").do(execute)


if __name__ == "__main__":
    run()
        