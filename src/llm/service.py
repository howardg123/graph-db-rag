from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from .schemas import Question
from .neo4j import Neo4j

from dotenv import load_dotenv

import os

load_dotenv()


class Service:
    def __init__(self) -> None:
        self.graphDB_instance = Neo4j(url=os.getenv("NEO4J_URI"), username=os.getenv(
            "NEO4J_USERNAME"), password=os.getenv("NEO4J_PASSWORD"))

    def populate_data(self):
        self.graphDB_instance.populate_data()
        return {"result": self.graphDB_instance.get_graph().schema}

    def choose_model(self, model: str = ""):
        if model == "llama":
            return OllamaLLM(model="llama3.1", temperature=0)

    def generate_response(self, question: Question) -> str:

        cypher_generation_template = """
        <Task>
        Generate Cypher query for a Neo4j graph database.
        </Task>
        <Instructions>
        Use only the provided relationship types and properties in the schema.
        Do not use any other relationship types or properties that are not provided.
        </Instructions>
        <Schema>
        {schema}
        </Schema>
        <Note>
        Do not include any explanations or apologies in your responses.
        Do not respond to any questions that might ask anything other than
        for you to construct a Cypher statement. Do not include any text except
        the generated Cypher statement. Make sure the direction of the relationship is
        correct in your queries. Make sure you alias both entities and relationships
        properly. Do not run any queries that would add to or delete from
        the database. Make sure to alias all statements that follow as with
        statement (e.g. WITH c as customer, o.orderID as order_id).
        If you need to divide numbers, make sure to
        filter the denominator to be non-zero.
        </Note>
        <Examples>
        # Retrieve the total number of orders placed by each customer.
        MATCH (c:Customer)-[o:ORDERED_BY]->(order:Order)
        RETURN c.customerID AS customer_id, COUNT(o) AS total_orders
        # List the top 5 products with the highest unit price.
        MATCH (p:Product)
        RETURN p.productName AS product_name, p.unitPrice AS unit_price
        ORDER BY unit_price DESC
        LIMIT 5
        # Find all employees who have processed orders.
        MATCH (e:Employee)-[r:PROCESSED_BY]->(o:Order)
        RETURN e.employeeID AS employee_id, COUNT(o) AS orders_processed
        String category values:
        Use existing strings and values from the schema provided. 
        </Examples>
        <Question>
        {question}
        </Question>
        """

        qa_generation_template_str = """
        <Task>
        You are an assistant that takes the results from a Neo4j Cypher query and forms a human-readable response. The query results section contains the results of a Cypher query that was generated based on a user's natural language question. The provided information is authoritative; you must never question it or use your internal knowledge to alter it. Make the answer sound like a response to the question.
        </Task>
        <Query Results>
        {context}
        </Query Results>
        <Question>
        {question}
        </Question>
        <Note>
        If the provided information is empty, respond by stating that you don't know the answer. Empty information is indicated by: []
        Output only in JSON format provided by the query results. Do not include any string before and after the JSON output.
        If the information is not empty, you must provide an answer using the results. If the question involves a time duration, assume the query results are in units of days unless specified otherwise.
        When names are provided in the query results, such as hospital names, be cautious of any names containing commas or other punctuation. For example, 'Jones, Brown and Murray' is a single hospital name, not multiple hospitals. Ensure that any list of names is presented clearly to avoid ambiguity and make the full names easily identifiable.
        Never state that you lack sufficient information if data is present in the query results. Always utilize the data provided.
        </Note>
        """

        llm = self.choose_model(question.model)

        graph_db = self.graphDB_instance.get_graph()

        cypher_generation_prompt = PromptTemplate(
            input_variables=["schema", "question"], template=cypher_generation_template
        )

        qa_generation_prompt = PromptTemplate(
            input_variables=["context", "question"], template=qa_generation_template_str
        )

        chain = GraphCypherQAChain.from_llm(
            top_k=100,
            graph=graph_db,
            verbose=True,
            validate_cypher=True,
            qa_prompt=qa_generation_prompt,
            cypher_prompt=cypher_generation_prompt,
            qa_llm=llm,
            cypher_llm=llm,
            allow_dangerous_requests=True
        )

        response = chain.invoke(
            {question.question})

        return response.get("result", "")
