import os

class FilesPath:
    @staticmethod
    def get() -> list:
        base_path = os.path.normpath(os.path.join(os.getcwd(), "insumosObras/arquivos"))
        if os.path.basename(base_path):
            def add_files(path):
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
            return add_files("patrimar") + add_files("novolar")
        return []
        
if __name__ == "__main__":
    print(FilesPath.get())