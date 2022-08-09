import os
import json
import string
import random
from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":

    if "secrets.json" not in os.listdir():
        with open("secrets.json", "w") as f:
            f.write(
                json.dumps(
                    {
                        "TWILIO_ACCOUNT_SID": "".join(
                            random.choice(string.ascii_lowercase + string.digits)
                            for _ in range(25)
                        ),
                        "TWILIO_AUTH_TOKEN": "".join(
                            random.choice(string.ascii_lowercase + string.digits)
                            for _ in range(25)
                        ),
                        "SECRET_KEY": get_random_secret_key(),
                        "ALLOWED_HOSTS": ["localhost", "127.0.0.1"],
                        "DEBUG": True,
                        "TWILIO_PHONE_NUMBER": "1" + "".join(random.choice(string.digits) for _ in range(9)),
                        "USER_NAME": "".join(random.choice(string.ascii_lowercase) for _ in range(15)),
                        "SP_USERNAME": "".join(random.choice(string.ascii_letters) for _ in range(5)) + "@nowhere.org",
                        "SP_PASSWORD": "".join(random.choice(string.ascii_letters) for _ in range(20)),
                    }
                )
            )
