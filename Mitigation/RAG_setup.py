import pandas as pd
from langchain_chroma import Chroma
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import os

data_path = os.path.join(os.getcwd(), "Data")
data_file = os.path.join(data_path, "RAG_data.jsonl")

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

df = pd.read_json(data_file, lines=True)
df.rename(columns={0:'descriptions'}, inplace=True)
df.drop_duplicates(inplace=True)
loader = DataFrameLoader(df, page_content_column="descriptions")

######### Only need to do this once
######### Comment the next two lines out after vector database has been saved
#data = loader.load()
########## Saves DB
#db = Chroma.from_documents(data, embedding_function, persist_directory="./db")

#### Loads DB
db = Chroma(persist_directory="./db", embedding_function=embedding_function)

#Example query only
query = "What package would be useful for efficient linear algebra operations on large matrices"

result = db.similarity_search_with_score(query, 10)

quote = " ".join(item[0].page_content for item in result)

print(quote)

######## Alternative method
embed = embedding_function.embed_query(query)
result2 = db.similarity_search_by_vector(embed, k=10)
print(result2)

