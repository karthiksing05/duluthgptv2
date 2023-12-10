import os
from PyPDF2 import PdfReader
import docx  #pip install python-docx
import text_generation

import utils

from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference

# os.environ["HUGGINGFACEHUB_API_TOKEN"] = "test"

############ TEXT LOADERS ############
# Functions to read different file types
def read_pdf(file_path):
    with open(file_path, "rb") as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def read_word(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text

def read_documents_from_directory(directory):
    combined_text = ""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith(".pdf"):
            combined_text += read_pdf(file_path)
        elif filename.endswith(".docx"):
            combined_text += read_word(file_path)
        elif filename.endswith(".txt"):
            combined_text += read_txt(file_path)
    return combined_text


train_directory = 'docs/'
text = read_documents_from_directory(train_directory)

char_text_splitter = CharacterTextSplitter(separator="\n", chunk_size=800, 
                                    chunk_overlap=200, length_function=len)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
    cache_folder=os.getcwd() + "\embeddings"
)

text_chunks = char_text_splitter.split_text(text)

docsearch = FAISS.from_texts(text_chunks, embeddings)

retriever = docsearch.as_retriever(lambda_val=0.025, k=2, filter=None)

llm = HuggingFaceTextGenInference(
    inference_server_url="https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-alpha",
    max_new_tokens=300,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
)

def askQuestion(query):

    # regenerating next couple events
    utils.updateCalendarEvents()

    docsLst = retriever.get_relevant_documents(query)
    docStr = "".join([doc.page_content + "\n\n" for doc in docsLst])
    docStr = "Context:\n\n" + docStr
    docStr += f"\n\nNote: if there is no relevant information given to you in the context, do not answer this question with outside information. Say I don't know and tell the student to find an admin.\n\nQuestion: {query}\nAnswer:"

    # try:
    data = llm(docStr)
    # except text_generation.errors.UnknownError:
    #     return "DuluthGPT couldn't generate a proper response: try asking the question in a different way!"

    data = data[:data.rfind(".")]
    data += "."

    postprocessStems = [
        "\nThe answer to the question",
        "\nPlease select one of the following",
        "\nAdditional Information:",
        "\nI don't know",
        "\nYou don't know the answer to this question",
        "\nTherefore, the answer to the rephrased question is:",
        "\nQuestion",
        "\nAnother Helpful Answer",
        "\nHelpful Answer",
        "\nUnhelpful Answer",
        "\nYou don't know the answer",
        "\nPolite Answer",
        "\nPlease answer",
        "\nWhat",
        "\nAgain"
    ]

    data = data.strip()
    for stem in postprocessStems:
        data = data.split(stem)[0]

    data = data.strip()

    return data

if __name__ == "__main__":

    while True:
        query = input("Ask a Question! ")
        if query == "exit":
            exit()

        print(askQuestion(query))
