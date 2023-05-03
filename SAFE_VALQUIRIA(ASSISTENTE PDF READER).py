print("=========================================")
print("SAFE_VALQUIRIA(ASSISTENTE PDF READER)")
print("=========================================")
#este programa ler arquivos em PDF e permite que você faça perguntas.
import warnings
import io
import os
import PyPDF2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.credentials import Credentials
import langchain
from langchain.text.character_splitting import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

os.environ["OPENAI_API_KEY"] = "sua chave"

print("verificando se o arquivo de credencial existe..")
credentials_path = "C:/Users/w/Downloads/credenciais.json"
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
try:
    response = service.files().get_media(fileId=file_id).execute()
    with open(output_file, 'wb') as f:
        f.write(response)
    print("Download concluído!")
    with open(output_file, 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        raw_text = ''
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                raw_text += text

        texts = text_splitter.split_text(raw_text)
        print("Conteúdo do arquivo PDF extraído com sucesso!")
except HttpError as error:
    print(f'Ocorreu um erro: {error}') 

raw_text = ''
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        raw_text += text

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
