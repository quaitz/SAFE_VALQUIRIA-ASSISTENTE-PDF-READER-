print("=========================================")
print("ASSISTENTE PDF READER SAFE VALQUIRIA")
print("=========================================")
import warnings
import io
import os
import PyPDF2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.credentials import Credentials

warnings.filterwarnings("ignore")
os.environ["OPENAI_API_KEY"] = "" #hugging key permission read ou write don't work, openai's key returns -> openai.error.RateLimitError: You exceeded your current quota, please check your plan and billing details.
print("verificando se o arquivo de credencial existe..")
credentials_path = "A:/VALQUIRIA/credenciais.json"
if not os.path.exists(credentials_path):
    print("Arquivo de credenciais não encontrado.")
    exit()
print("definindo escopo de acesso a API do Google Drive..")
scopes = ['https://www.googleapis.com/auth/drive']
print("carregando as credenciais a partir do arquivo JSON..")
creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
print("criando um objeto de serviço do Google Drive..")
service = build('drive', 'v3', credentials=creds)
print("testando a conexão do Google Drive..")
try:
    files = service.files().list().execute()
    print("Conexão com o Google Drive realizada com sucesso!")
except Exception as e:
    print(f"Erro ao conectar o Google Drive: {e}")
    exit()
print("Definindo o nome da pasta e do arquivo a serem buscados..")
folder_name = "langchain"
file_name = input("Digite o nome do arquivo com extensão: ")
print("Realizando a busca pelas pastas")
results = service.files().list(q="mimeType='application/vnd.google-apps.folder'", fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])
print("Imprimindo as pastas encontradas")
if not items:
    print('Nenhuma pasta encontrada.')
else:
    print('Pastas:')
    for item in items:
        print(u'{0} ({1})'.format(item['name'], item['id']))





print("Buscando o ID da pasta a partir do seu nome..")
query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
folder_id = None
results = service.files().list(q=query).execute()
items = results.get('files', [])
if items:
    folder_id = items[0]['id']
print("Imprimindo a variável folder_id na próxima linha")
print(folder_id)
print("Buscando o ID do arquivo..")
file_id = None
query = f"'{folder_id}' in parents and name='{file_name}' and mimeType='application/pdf'"
print(query)
print("Query definido..")
try:
    results = service.files().list(q=query).execute()
    items = results.get('files', [])
    if items:
        file_id = items[0]['id']
        print(f"ID do arquivo encontrado: {file_id} ..")
except Exception as e:
    print(f"Erro ao buscar o ID do arquivo {file_name}: {e}")
    exit()
print(f"Caminho do arquivo: My Drive/{folder_name}/{file_name} ..")
print("Fazendo download do conteúdo do arquivo..")




#output_file = f"My Drive/{folder_name}/{file_name}"
#(correto seria)output_file = f"My Drive\\{folder_name}\\{file_name}"
#print(f"***output_file: {output_file}***")
#"você pode definir output_file como file_path para usar o caminho completo do arquivo como o nome do arquivo de saída para o arquivo PDF."
#from langchain.text.character_splitting import CharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
#from langchain.qa.chains import load_qa_chain



#20230506
# Get file metadata
file = service.files().get(fileId=file_id, fields='parents').execute()
# Get parent folders
parents = file.get('parents')
# Get folder metadata for the first parent folder
folder_id = parents[0]
folder = service.files().get(fileId=folder_id, fields='name, parents').execute()
# Get parent folders for the first parent folder
parents = folder.get('parents')
# Iterate through parent folders until you reach the root folder
while parents: #nesse trecho de código a variável parents é uma lista que contém os IDs dos diretórios pai, enquanto a variável parent é um dicionário que contém informações sobre um diretório pai específico. O loop percorre a lista de IDs dos diretórios pai (parents) e obtém informações do diretório pai atual (parent) a partir do ID atual da lista (parent_id). Quando o diretório pai atual não tem mais um pai, ou seja, quando é a raiz do diretório, o loop é interrompido.
    parent_id = parents[0]
    parent = service.files().get(fileId=parent_id, fields='name, parents').execute()
    if 'root' in parent.get('parents', []):
        break
    parents = parent.get('parents')
# Get the full path of the file
#file_path = '/'.join([parents.get('name'), folder.get('name'), file.get('name')])
print(f"***(*_*)_ definindo caminho para variavel file_path***")
#file_path = '/'.join([parents[0].get('name'), folder.get('name'), file.get('name')])
if parents and parents[0]:
   # file_path = '/'.join([parents[0].get('name'), folder.get('name'), file.get('name')])
#    file_path = '/'.join([parents[0].get('name'), folder.get('name'), file.get('name')])
#    file_path = file_path.replace('My Drive', 'My\ Drive')
#    file_path = "G:/My Drive/" + folder.get('name') + "/" + file.get('name')
    file_path = f'G:/My Drive/{folder.get("name")}/{file.get("name")}'
else:
    # Tratar o caso em que parents está vazio ou parents[0] é None
    print("(*_*)_ A variável parents é None, ou seja, não está apontando para nenhum objeto. Talvez o ID do arquivo que você está tentando acessar não tenha nenhum pai associado a ele, o que significa que file.get('parents') retornou None.")
    print("(*_*)_ A definição do caminho falou, mas já inserimos o caminho G:\My Drive\langchain pra você, insira apenas o nome do arquivo.")
    file_path = f"G:/My Drive/langchain/{input('Digite o nome do arquivo com extensão: ')}"
print(f"***imprimindo file_path: {file_path}***")
# Download the file
request = service.files().get_media(fileId=file_id)
with open(file_path, 'wb') as f:
    f.write(request.execute())



# Extract text from the PDF file
#text_splitter = CharacterTextSplitter(min_text_length=10)
#narnia\Lib\site-packages\langchain\text_splitter.py", line 194, in __init__ super().__init__(**kwargs) TypeError: TextSplitter.__init__() got an unexpected keyword argument 'min_text_length'
#Uma possível solução seria remover o parâmetro min_text_length da chamada do construtor da classe CharacterTextSplitter.
#Se quiser especificar um valor diferente para esse parâmetro, verifique a documentação da classe CharacterTextSplitter para encontrar o nome correto do parâmetro.
text_splitter = CharacterTextSplitter()
with open(file_path, 'rb') as f:
#    reader = PyPDF2.PdfFileReader(f)
#PyPDF2.errors.DeprecationError: PdfFileReader is deprecated and was removed in PyPDF2 3.0.0. Use PdfReader instead. -> Para corrigir o problema, altere a linha que menciona o PdfFileReader para mencionar o PdfReader.
    reader = PyPDF2.PdfReader(f)
    raw_text = ''
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text
    texts = text_splitter.split_text(raw_text)
print("Conteúdo do arquivo PDF extraído com sucesso!")
#20230506








raw_text = ''.join([page.extract_text() for page in reader.pages if page.extract_text()])
text_splitter = CharacterTextSplitter(        
    separator = "\n",
    chunk_size = 1000,
    chunk_overlap  = 200,
    length_function = len,
)
texts = text_splitter.split_text(raw_text)
print("Número de blocos de texto extraídos:", len(texts))
print("Criando o índice de busca por similaridade..")
embeddings = OpenAIEmbeddings()
docsearch = FAISS.from_texts(texts, embeddings)
print("Preparando o modelo de perguntas e respostas..")
chain = load_qa_chain(OpenAI(), chain_type="stuff")
while True:
    query = input("Faça uma pergunta sobre o arquivo: ")
    if query.lower() in ["sair", "exit", "quit"]:
        break
    docs = docsearch.similarity_search(query)
    chain.run(input_documents=docs, question=query)
print("Programa encerrado.") 
