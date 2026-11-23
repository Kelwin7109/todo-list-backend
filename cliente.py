"""Cliente mínimo: autentica e consulta as análises do usuário."""

from getpass import getpass

import requests


URL_API = "http://127.0.0.1:8000"


def main() -> None:
    email = input("E-mail: ")
    senha = getpass("Senha: ")

    login = requests.post(
        f"{URL_API}/usuarios/login",
        json={"email": email, "senha": senha},
        timeout=10,
    )
    login.raise_for_status()
    token = login.json()["accessToken"]

    analytics = requests.get(
        f"{URL_API}/tasks/analytics",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    analytics.raise_for_status()
    print(analytics.text)


if __name__ == "__main__":
    main()
