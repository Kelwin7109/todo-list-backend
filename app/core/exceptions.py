"""Exceções de domínio."""


class ErroDeDominio(Exception):
    """Classe base de todo erro previsto de negócio."""

    mensagem = "Não foi possível concluir a operação."

    def __init__(self, mensagem: str | None = None) -> None:
        self.mensagem = mensagem or type(self).mensagem
        super().__init__(self.mensagem)


# Recurso inexistente — a camada HTTP traduz esta família em 404.
class RecursoNaoEncontrado(ErroDeDominio):
    """Pediriam um registro que não existe."""

    mensagem = "Recurso não encontrado."


class UsuarioNaoEncontrado(RecursoNaoEncontrado):
    mensagem = "Usuário não encontrado."


# Regra de negócio inválida — a camada HTTP traduz esta família em 422.
class RegraDeNegocioViolada(ErroDeDominio):
    """A operação é compreensível, mas contraria uma regra do negócio."""

    mensagem = "Operação recusada por uma regra de negócio."


class ValorInvalido(RegraDeNegocioViolada):
    """Valor fora do conjunto aceito para um campo do domínio."""

    mensagem = "Valor inválido para o campo."


# Conflito e autenticacao — traduzidos em 409 e 401.
class EmailJaCadastrado(ErroDeDominio):
    """Um e-mail não pode ser usado por dois usuários.

    A mensagem é a mesma que o front-end já exibe hoje no cadastro.
    """

    mensagem = "Já existe uma conta com este e-mail."


class NaoAutenticado(ErroDeDominio):
    """Família dos erros de identidade — a camada HTTP traduz em 401."""

    mensagem = "É preciso entrar na conta para continuar."


class CredenciaisInvalidas(NaoAutenticado):
    """Indica que o e-mail não existe ou a senha está incorreta."""

    mensagem = "E-mail ou senha incorretos."


class TokenInvalido(NaoAutenticado):
    """Token de acesso ausente, expirado, adulterado ou de usuário removido."""

    mensagem = "Sessão inválida. Entre novamente."
