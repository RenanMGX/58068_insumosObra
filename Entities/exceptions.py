class SheetNotFoundError(Exception):
    """
    Exceção levantada quando uma planilha específica não é encontrada.
    """
    def __init__(self, *args: object) -> None:
        """
        Inicializa a exceção SheetNotFoundError.
        
        Args:
            *args (object): Argumentos adicionais para a exceção.
        """
        super().__init__(*args)
        
class ColumnNotFoundError(Exception):
    """
    Exceção levantada quando uma coluna específica não é encontrada.
    """
    def __init__(self, *args: object) -> None:
        """
        Inicializa a exceção ColumnNotFoundError.
        
        Args:
            *args (object): Argumentos adicionais para a exceção.
        """
        super().__init__(*args)