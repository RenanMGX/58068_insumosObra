import os

class FilesPath:
    @staticmethod
    def get() -> list:
        """
        Obtém a lista de arquivos Excel (.xlsx, .xls, .xlsm) nos diretórios especificados.
        
        Returns:
            list: Lista de caminhos para os arquivos encontrados.
        """
        base_path = os.path.normpath(os.path.join(os.getcwd(), "insumosObras/arquivos"))
        if os.path.basename(base_path):
            def add_files(path):
                """
                Adiciona arquivos de um diretório específico à lista de resultados.
                
                Args:
                    path (str): Caminho relativo do diretório a ser verificado.
                
                Returns:
                    list: Lista de caminhos para os arquivos encontrados no diretório.
                """
                path = os.path.join(base_path, path)
                if not os.path.exists(path):
                    raise FileNotFoundError(f"{path=} não existe!")
                result = []
                for file in os.listdir(path):
                    file = os.path.join(path, file)
                    if os.path.isfile(file):
                        if file.endswith(('.xlsx','.xls', 'xlsm')):
                            result.append(file)
                return result
            
            # Adiciona arquivos dos diretórios "patrimar" e "novolar"
            return add_files("patrimar") + add_files("novolar")
        return []
        
if __name__ == "__main__":
    # Exemplo de uso da classe FilesPath
    print(FilesPath.get())