from django.core.exceptions import ValidationError
import re

class Validador:
    """
    Classe base para os validadores.
    """
    def __init__(self, proximo_validador=None):
        self.proximo_validador = proximo_validador

    def validar(self, value, field_name):
        """
        Método para validar o valor de um campo.
        Deve ser implementado nas subclasses.

        Args:
            value: O valor a ser validado.
            field_name (str): O nome do campo que está sendo validado.

        Returns:
            None: Se a validação for bem-sucedida.

        Raises:
            ValidationError: Se a validação falhar.
        """
        if self.proximo_validador:
            self.proximo_validador.validar(value, field_name)

class ValidadorNome(Validador):
    def validar(self, value, field_name):
        super().validar(value, field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field_name} deve ser uma string não vazia.")

class ValidadorIdade(Validador):
    def validar(self, value, field_name):
        super().validar(value, field_name)
        if not isinstance(value, int):
            raise ValidationError(f"{field_name} deve ser um número inteiro.")
        if value <= 0 or value > 125:
            raise ValidationError(f"{field_name} deve estar entre 0 e 125.")

class ValidadorSexo(Validador):
    def validar(self, value, field_name):
        super().validar(value, field_name)
        if not isinstance(value, str) or value not in ["M", "F"]:
            raise ValidationError(f"{field_name} deve ser 'M' ou 'F'.")

class ValidadorEstadoCivil(Validador):
    def validar(self, value, field_name):
        super().validar(value, field_name)
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} deve ser uma string.")

class ValidadorTipoSanguineo(Validador):
    def validar(self, value, field_name):
        super().validar(value, field_name)
        if not isinstance(value, str) or value not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            raise ValidationError(f"{field_name} inválido.")