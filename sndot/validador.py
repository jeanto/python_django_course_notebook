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
        if not isinstance(value, str) or not value.strip() or not value.replace(" ", "").isalpha():
            raise ValidationError(f"{field_name} deve ser uma string não vazia e conter apenas letras.")

class ValidadorScriptInjection(Validador):
    def validar(self, value, field_name):
        super().validar(value, field_name)
        if re.search(r'<script.*?>.*?</script>', value, re.IGNORECASE):
            raise ValidationError(f"{field_name} contém tags de script e não é permitido.")

class ValidadorXSS(Validador):
    def validar(self, value, field_name):
        super().validar(value, field_name)
        if re.search(r'<[^>]+>', value):
            raise ValidationError(f"{field_name} contém tags HTML e não é permitido.")
        
### https://regex101.com/r/qE9gR7/1
class ValidadorSQLInjection(Validador):
    def validar(self, value, field_name):
        super().validar(value, field_name)

        regex = r"(\s*([\0\b\'\"\n\r\t\%\_\\]*\s*(((select\s*.+\s*from\s*.+)|(insert\s*.+\s*into\s*.+)|(update\s*.+\s*set\s*.+)|(delete\s*.+\s*from\s*.+)|(drop\s*.+)|(truncate\s*.+)|(alter\s*.+)|(exec\s*.+)|(\s*(all|any|not|and|between|in|like|or|some|contains|containsall|containskey)\s*.+[\=\>\<=\!\~]+.+)|(let\s+.+[\=]\s*.*)|(begin\s*.*\s*end)|(\s*[\/\*]+\s*.*\s*[\*\/]+)|(\s*(\-\-)\s*.*\s+)|(\s*(contains|containsall|containskey)\s+.*)))(\s*[\;]\s*)*)+)"

        if re.search(regex, value, re.IGNORECASE):
            raise ValidationError(f"{str(field_name).title()} contém caracteres que podem ser usados para injeção SQL.")
        


