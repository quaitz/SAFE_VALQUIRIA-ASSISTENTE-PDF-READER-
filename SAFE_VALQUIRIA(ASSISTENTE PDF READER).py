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
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

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


caminho_do_arquivo = f"G:/My Drive/langchain/{input('Digite o nome do arquivo com extensão: ')}"
with open(caminho_do_arquivo, 'rb') as f:
    reader = PdfReader(f)

reader = PdfReader(caminho_do_arquivo)
reader
raw_text = ''
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        raw_text += text

print("Conteúdo do arquivo PDF extraído com sucesso!")

#20230506
raw_text[:100]

text_splitter = CharacterTextSplitter(        
    separator = "\n",
    chunk_size = 1000,
    chunk_overlap  = 200,
    length_function = len,
)
texts = text_splitter.split_text(raw_text)
print("Número de blocos de texto extraídos:", len(texts))

#20230506
len(texts)
#returns: "Número de blocos de texto extraídos"

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
