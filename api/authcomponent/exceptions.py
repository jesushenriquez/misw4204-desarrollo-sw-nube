class UsuarioNoExiste(Exception):
    def __init__(self, message="El usuario no existe"):
        self.message = message
        super().__init__(self.message)

class UsuarioYaExiste(Exception):
    def __init__(self, message="El usuario ya existe"):
        self.message = message
        super().__init__(self.message)