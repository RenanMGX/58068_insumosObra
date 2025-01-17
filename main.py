from Entities.tratar_dados import TratarDados, pd
from Entities.get_files import FilesPath
from Entities.dependencies.arguments import Arguments
import os
from Entities.dependencies.functions import P

class Execute:
    converFile_path = r"C:\Users\renan.oliveira\PATRIMAR ENGENHARIA S A\RPA - Documentos\RPA - Dados\Relatorios\Insumos de Obras - Qualidade\Materiais Aplicados - Conversão.xlsx"
    finalFile_path = r"C:\Users\renan.oliveira\PATRIMAR ENGENHARIA S A\RPA - Documentos\RPA - Dados\Relatorios\Insumos de Obras - Qualidade"
    
    @staticmethod
    def start():
        if not os.path.exists(Execute.finalFile_path):
            raise FileNotFoundError(f"{Execute.finalFile_path=} não existe!")
        
        dfs = TratarDados.preprar(lista=FilesPath.get(), tabela_base=Execute.converFile_path)
        
        df = pd.concat(dfs)
        
        df.to_excel(os.path.join(Execute.finalFile_path, "Relatorio_Final.xlsx"), index=False)
        
        print(P("Concluido!"))
    
if __name__ == "__main__":
    Arguments({
        "start" : Execute.start,
    })