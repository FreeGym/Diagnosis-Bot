import os
import os.path
from llama_index import VectorStoreIndex,StorageContext,load_index_from_storage,download_loader
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
import logging
import sys
from llama_index.llms import OpenAI
from llama_index import ServiceContext

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Run the following commands 
# conda activate diagnosis_bot
# pip install llama-index 
openai.api_key=os.getenv("OPENAI_API_KEY")

llm = OpenAI(temperature=0.5, model="gpt-3.5-turbo")
service_context = ServiceContext.from_defaults(llm=llm)

# check if storage already exists
PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    # load the documents and create the index
    ObsidianReader = download_loader('ObsidianReader')
    #Insert the path of your obsidian vault here
    documents = ObsidianReader("Autogen_Blogs/Blogs (1)").load_data() # Returns list of documents
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

# either way we can now query the index
query_engine = index.as_query_engine()

prompt = """
            """
response = query_engine.query(prompt)
print(response)


with open("context.txt","w") as file:
    file.write(str(response))