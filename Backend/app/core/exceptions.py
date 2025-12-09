# Custom Exceptions für MuDiKo

class MuDiKoException(Exception):
    """Basis-Exception für alle Custom Exceptions."""
    pass

class SessionNotFoundException(MuDiKoException):
    """Session wurde nicht gefunden."""
    pass

class SessionExpiredException(MuDiKoException):
    """Session ist abgelaufen."""
    pass

class InvalidFileFormatException(MuDiKoException):
    """Ungültiges Dateiformat."""
    pass

class PluginNotFoundException(MuDiKoException):
    """Plugin wurde nicht gefunden."""
    pass

class PluginInitializationException(MuDiKoException):
    """Fehler beim Initialisieren eines Plugins."""
    pass
