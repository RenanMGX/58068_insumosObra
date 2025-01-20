from Entities.tratar_dados import TratarDados, pd
from Entities.get_files import FilesPath
from Entities.dependencies.arguments import Arguments
import os
from Entities.dependencies.functions import P, Functions
from getpass import getuser

class Execute:
    converFile_path = FilesPath.get_covertFile()
    finalFile_path = FilesPath.get_finalFile_path()
    
    @staticmethod
    def start():
        if not os.path.exists(Execute.finalFile_path):
            raise FileNotFoundError(f"{Execute.finalFile_path=} não existe!")
        
        dfs = TratarDados.preprar(lista=FilesPath.get(), tabela_base=Execute.converFile_path)
        
        df = pd.concat(dfs)
        df = df.drop_duplicates()
        
        final_path = os.path.join(Execute.finalFile_path, "Relatorio_Final.xlsx")
        Functions.fechar_excel(final_path)
        
        for file in os.listdir(Execute.finalFile_path):
            file = os.path.join(Execute.finalFile_path, file)
            if os.path.isfile(file):
                os.remove(file)
                
                
        df.to_excel(final_path, index=False)
        
        print(P("Concluido!"))
    
if __name__ == "__main__":
    Arguments({
        "start" : Execute.start,
    })