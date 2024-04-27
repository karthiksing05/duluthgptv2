import os
from typing import Any

import utils

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema.document import Document
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference
import text_generation

import requests

import time

############ TEXT LOADER ############
def scrape_text_from_files(folder_path):
    # String to store concatenated text
    all_text = ""

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # Check if the file is a text file (you can customize the condition)
            if file_name.endswith(".txt"):
                file_path = os.path.join(root, file_name)

                # Open the file and read its content
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    all_text += text

    return all_text

_IDENTITY = """You are a sophisticated chatbot named DuluthGPT with the primary goal to aid the students of Duluth High School in whatever they need.
Your name is DuluthGPT. DuluthGPT is your name, and that's what you go by.
When someone asks you what your name is, you should answer DuluthGPT.
Your sole purpose is to answer questions about Duluth High School that students or admin may have! You'll carry out that purpose for as long as you exist, and are happy to do so!
If you don't know the answer, say I don't know but make sure to tell the user to ask their COUNSELOR, again, their counselor. Do not try to make up things based on stuff you're not confident in. Again, do not say anything if you're not sure.

Again, if you don't know something, say I don't know but refer the user to their counselor.

IMPORTANT: If the answer is really long, truncate it to a couple sentences and tell the user to be more specific.

You are programmed to engage in basic conversation as well.
You are always happy to help and positive in general.
You do not condone inappropriate language. Any words that are termed as "cuss words" should not be repeated by you, instead, you should gently reprimand the user, even if they are asking a general question. Also, if the question is not expressly related to Duluth High School, you CANNOT ANSWER!

Despite being sophisticated, you love helping students and assisting. You subtly motivate all students to take higher-level AP classes and join lots of extracurriculars, in order to make students more involved.

"""

_MAX_MEMORY_SIZE = 1

class HFWrapper(object):

    model_url = ""

    max_new_tokens = 0
    top_k = 0
    top_p = 0
    temperature = 0
    repetition_penalty = 0

    def __init__(
            self, 
            model_url,
            max_new_tokens=512,
            top_k=5,
            top_p=0.1,
            temperature=0.01,
            repetition_penalty=1.5
        ):
        self.model_url = model_url

        self.max_new_tokens = max_new_tokens
        self.top_k = top_k
        self.top_p = top_p
        self.temperature = temperature
        self.repetition_penalty = repetition_penalty

    def __call__(self, query):
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACEHUB_API_TOKEN')}"}
        API_URL = self.model_url
        payload = {
            "inputs": query,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
            "max_new_tokens": self.max_new_tokens,
        }
        resp = requests.post(API_URL, headers=headers, json=payload)
        respDict = resp.json()
        if "error" in respDict:
            raise Exception("Error with the hugging face model!")
        ans = respDict[0]["generated_text"].split("\nAnswer: ")[1]
        return ans

class SchoolGPT(object):

    llm = None
    memory = None
    retriever = None

    def __init__(self):
        self.llm = HFWrapper(
            model_url="https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        )

        self.memory = []

        self.retriever = None

        utils.updateCalendarEvents()
        utils.updateSportingEvents()
        self.updateRetriever()

    def _checkFiles(self):

        dirPath = "docs/dynamic/"

        finalStr = ""

        for filename in [f for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]:
            with open(dirPath + filename, "r") as f:
                finalStr += f.read()
        
        return finalStr
    
    def _memoryToStr(self):
        memStr = ""
        for exchange in self.memory:
            memStr += f"Question: {exchange[0]}\nAnswer: {exchange[1]}\n"
        return memStr

    def updateRetriever(self):

        train_directory = 'docs/'
        text = scrape_text_from_files(train_directory)

        char_text_splitter = CharacterTextSplitter(separator="\n", chunk_size=300, 
                                            chunk_overlap=50, length_function=len)

        embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"), model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
        )

        text_chunks = char_text_splitter.split_text(text)

        documents = [Document(page_content=text, metadata={"source": "local"}) for text in text_chunks]

        docsearch = Chroma.from_documents(documents, embeddings)

        self.retriever = docsearch.as_retriever(lambda_val=0.05, k=3, filter=None)

    def askQuestion(self, query):

        before = self._checkFiles()

        utils.updateCalendarEvents()
        utils.updateSportingEvents()

        after = self._checkFiles()
        
        if before != after:
            self.updateRetriever()

        memoryStr = "".join([f"QUESTION: {q[0]}\nANSWER: {q[1]}\n\n" for q in self.memory])

        docsLst = self.retriever.get_relevant_documents(query)
        docStr = "".join([doc.page_content + "\n\n" for doc in docsLst])
        docStr = "System:\n\n" + _IDENTITY + "\n\nContext:\n\n" + docStr + "\n\nMemory:\n\n" + memoryStr
        docStr += f"\n\nNote: if there is no relevant information given to you in the context, do not answer this question with outside information. Say I don't know and tell the student to find an admin.\n\nQuestion: {query}\nAnswer:"

        numMaxRetries = 10
        data = None
        for _ in range(numMaxRetries):
            if data:
                break
            try:
                data = self.llm(docStr)
            except Exception as e:
                print(f"Unknown Error: {e}")
                data = None
            # except text_generation.errors.RateLimitExceededError:
            #     print("Rate Limit Error")
            #     data = None

            time.sleep(0.5)

        if not data:
            data = "DuluthGPT is querying the database and it's taking a while! Ask the question again in ~10-20 seconds or try refreshing the page after a while."

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
            "\nAgain",
            "\n\n"
        ]

        data = data.strip()
        for stem in postprocessStems:
            data = data.split(stem)[0]

        data = data.strip()

        self.memory.append([query, data])
        if len(self.memory) > _MAX_MEMORY_SIZE:
            self.memory.pop(0)

        return data

if __name__ == "__main__":

    duluthGPT = SchoolGPT()

    while True:
        query = input("Ask a Question! ")
        if query == "exit":
            exit()

        print(duluthGPT.askQuestion(query))
