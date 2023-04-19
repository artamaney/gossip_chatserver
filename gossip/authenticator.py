import json

import bcrypt
from pydantic import BaseSettings


class AuthenticatorSettings(BaseSettings):
    file = "tokens.json"

    class Config:
        env_prefix = "AUTHENTICATOR_"


class Authenticator:
    def __init__(self, settings: AuthenticatorSettings):
        self._settings = settings

    def generate_token(self, password: str) -> str:
        password = password.encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt(10))
        return hashed.decode('utf-8')

    def save_token(self, username: str, token: str) -> None:
        with open(self._settings.file, "r") as f:
            content = f.read()
        json_file = json.loads(content)
        json_file[username] = token
        with open(self._settings.file, "w") as f:
            f.write(json.dumps(json_file))

    def check_user(self, username: str, password: str) -> bool:
        with open(self._settings.file, "r") as f:
            content = f.read()
        try:
            json_file = json.loads(content)
            if json_file.get(username) is not None and bcrypt.checkpw(password.encode('utf-8'),
                                                                      json_file[username].encode('utf-8')):
                return True
        except Exception:
            return False
        return False


if __name__ == "__main__":
    a = Authenticator(AuthenticatorSettings())
    print(a.generate_token("test"))