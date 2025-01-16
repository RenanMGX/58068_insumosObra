class SheetNotFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class ColumnNotFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)