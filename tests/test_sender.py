from pymail import EmailSender, email_on_error
import logging


logger = logging.basicConfig(level=logging.INFO)


def test_email_sender():
    sender = EmailSender()
    sender.send_message("test error from mac.")


@email_on_error(task_name="testing! testing! testing!", subject=None)
def test_error():
    raise Exception("A human-readable error message.")


if __name__ == "__main__":
    # test_email_sender()
    test_error()
