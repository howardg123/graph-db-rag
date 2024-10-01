from langchain.chains import GraphCypherQAChain
from langchain_core.prompts import ChatPromptTemplate
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
        self.graphDB_instance.populate_data_hr()
        return {"result": self.graphDB_instance.get_graph().schema}

    def delete_data(self):
        self.graphDB_instance.delete_data_hr()
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
        Always include id, full_name, position, department, tech_mentor, career_mentor, project.
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
        # Find the mentor of mentee
        Use the relationship IS_CAREER_MENTOR_OF or IS_TECH_MENTOR_OF and return all information
        # Find the mentees of mentor
        Use the relationship IS_CAREER_MENTEE_OF or IS_TECH_MENTEE_OF and return all information
        # Find the project and people who works on a project
        Use the relationship WORKS_ON and return all information including project name
        String category values:
        Use existing strings and values from the schema provided. 
        Do not use AS
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
        If the provided information is empty, respond by stating that you don't know the answer. Empty information is indicated by: []. If there is a cypher context provided, answer using the context.
        When names are provided in the query results, such as hospital names, be cautious of any names containing commas or other punctuation. For example, 'Jones, Brown and Murray' is a single hospital name, not multiple hospitals. Ensure that any list of names is presented clearly to avoid ambiguity and make the full names easily identifiable.
        Never state that you lack sufficient information if data is present in the query results. Always utilize the data provided.
        Only output relevant information and only use purely text in output formatting. Do not use newline. Just answer the question, do not write any irrelevant sentences. Do not include the question in the output.
        </Note>
        <Format>
        Question: Find is_tech_mentor_of William Hoover
        Answer: Bryan Wheeler is the tech mentor of William Hoover
        Question: Find is_tech_mentee_of Scott Stafford
        Answer: Tech mentee of Scott Stafford are: Bryan Wheeler, Kristin Johnson, Jeffery Dominguez
        Question: Find all person who works on Market Research Tool
        Answer: Employees who worked on Market Research Tool are: Bryan Wheeler, Kristin Johnson, Jeffery Dominguez
        Question: Find project of Bryan Wheeler
        Answer: Bryan Wheeler worked on Market Research Tool, and Digital Payment Integration
        </Format>
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

        rephrased_prompt = self.rephrase_prompt(question)

        response = chain.invoke(
            {rephrased_prompt})

        return response.get("result", "")

    def rephrase_prompt(self, question: Question) -> str:
        template = """
        <Note>
        Rephrase the question to one of the following and replace the name with the provided name in the context:
        Find is_career_mentor_of <name>
        Find is_tech_mentor_of <name>
        Find is_career_mentee_of <name>
        Find is_the_tech_mentee_of <name>
        Find the department of <name>
        Find the id of <name>
        Find the full_name of <name>
        Find the position of <name>
        Find all person who works_on <project>
        Find project of <name>
        </Note>
        <Question>
        {question}
        </Question>
        <Output format>
        Do not include any unnecessary sentences. Just output the rephrased question
        </Output format>
        """

        prompt = ChatPromptTemplate.from_template(template)

        chain = prompt | self.choose_model(question.model)

        response = chain.invoke(
            {question.question})

        return response
