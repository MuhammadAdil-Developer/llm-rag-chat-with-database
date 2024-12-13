import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SQLDatabase
from langchain.prompts import ChatPromptTemplate

def connectDatabase(username, port, host, password, database):
    mysql_uri = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
    st.session_state.db = SQLDatabase.from_uri(mysql_uri)

def runQuery(query):
    return st.session_state.db.run(query) if st.session_state.db else "Please connect to database"

def getDatabaseSchema():
    return st.session_state.db.get_table_info() if st.session_state.db else "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"

# Replace ChatOllama with ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key="your-openai-key")

def getQueryFromLLM(question):
    template = """below is the schema of MYSQL database, read the schema carefully about the table and column names. Also take care of table or column name case sensitivity.
    Finally answer user's question in the form of SQL query.

    {schema}

    please only provide the SQL query and nothing else

    for example:
    question: how many albums we have in database
    SQL query: SELECT COUNT(*) FROM album
    question: how many customers are from Brazil in the database ?
    SQL query: SELECT COUNT(*) FROM customer WHERE country=Brazil

    your turn :
    question: {question}
    SQL query :
    please only provide the SQL query and nothing else
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm

    response = chain.invoke({
        "question": question,
        "schema": getDatabaseSchema()
    })
    return response.content

def getResponseForQueryResult(question, query, result):
    template2 = """below is the schema of MYSQL database, read the schema carefully about the table and column names of each table.
    Also look into the conversation if available
    Finally write a response in natural language by looking into the conversation and result.

    {schema}

    Here are some example for you:
    question: how many albums we have in database
    SQL query: SELECT COUNT(*) FROM album;
    Result : [(34,)]
    Response: There are 34 albums in the database.

    question: how many users we have in database
    SQL query: SELECT COUNT(*) FROM customer;
    Result : [(59,)]
    Response: There are 59 amazing users in the database.

    question: how many users above are from india we have in database
    SQL query: SELECT COUNT(*) FROM customer WHERE country=india;
    Result : [(4,)]
    Response: There are 4 amazing users in the database.

    your turn to write response in natural language from the given result :
    question: {question}
    SQL query : {query}
    Result : {result}
    Response:
    """

    prompt2 = ChatPromptTemplate.from_template(template2)
    chain2 = prompt2 | llm

    response = chain2.invoke({
        "question": question,
        "schema": getDatabaseSchema(),
        "query": query,
        "result": result
    })

    return response.content

st.set_page_config(
    page_icon="🤖",
    page_title="AI-Powered MySQL Query Assistant",
    layout="centered"
)

# Add a heading to the page
st.title("🔧 AI-Powered MySQL Query Assistant")
st.subheader("chat your MySQL database with natural language")

question = st.chat_input('query with your database')

if "chat" not in st.session_state:
    st.session_state.chat = []

if question:
    if "db" not in st.session_state:
        st.error('Please connect to the database first.')
    else:
        st.session_state.chat.append({
            "role": "user",
            "content": question
        })

        query = getQueryFromLLM(question)
        print(query)
        result = runQuery(query)
        print(result)
        response = getResponseForQueryResult(question, query, result)
        st.session_state.chat.append({
            "role": "assistant",
            "content": response
        })

for chat in st.session_state.chat:
    st.chat_message(chat['role']).markdown(chat['content'])

with st.sidebar:
    st.title('Connect to Database')
    st.text_input(label="Host", key="host", value="10.10.20.127")
    st.text_input(label="Port", key="port", value="3306")
    st.text_input(label="Username", key="username", value="myadmin")
    st.text_input(label="Password", key="password", value="", type="password")
    st.text_input(label="Database", key="database", value="MyDB")
    connectBtn = st.button("Connect")

if connectBtn:
    connectDatabase(
        username=st.session_state.username,
        port=st.session_state.port,
        host=st.session_state.host,
        password=st.session_state.password,
        database=st.session_state.database,
    )

    st.success("Database connected")
