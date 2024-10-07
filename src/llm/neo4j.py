from langchain_community.graphs import Neo4jGraph


class Neo4j:
    def __init__(self, url: str, username: str, password: str) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.graphDB = Neo4jGraph(
            url=url, username=username, password=password)

    def get_graph(self):
        return self.graphDB

    def delete_data_hr(self):
        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]-()
        DELETE n,r
        """
        self.graphDB.query(query)
        self.graphDB.refresh_schema()
        return {"result": self.graphDB.schema}

    def populate_data_hr(self):
        query = """
        LOAD CSV WITH HEADERS FROM 'https://chm-ahgd001-dev-data-storage-assets.s3.ap-southeast-1.amazonaws.com/assets/product_urls/data.csv' AS row
        MERGE (p:Person {id: row.id, full_name: row.full_name})
        SET p.position = row.position,
            p.department = row.department,
            p.career_mentor = row.career_mentor,
            p.tech_mentor = row.tech_mentor,
            p.project = row.project

        WITH p, row
        WHERE row.career_mentor IS NOT NULL AND trim(row.career_mentor) <> p.full_name
        MERGE (c:Person {full_name: trim(row.career_mentor)})
        MERGE (c)-[:IS_CAREER_MENTOR_OF]->(p)
        MERGE (p)-[:IS_CAREER_MENTEE_OF]->(c)
        WITH p, row
        WHERE row.tech_mentor IS NOT NULL
        MERGE (t:Person {full_name: trim(row.tech_mentor)})
        MERGE (t)-[:IS_TECH_MENTOR_OF]->(p)
        MERGE (p)-[:IS_TECH_MENTEE_OF]->(t)
        WITH p, row
        WHERE row.project IS NOT NULL AND row.project <> 'None'
        WITH p, replace(replace(replace(row.project, "[", ""), "]", ""), "'", "") AS cleaned_projects
        WITH p, split(cleaned_projects, ', ') AS projects
        UNWIND projects AS project_name
        MERGE (proj:Project {name: trim(project_name)})
        MERGE (p)-[:WORKS_ON]->(proj)
        """
        self.graphDB.query(query)
        self.graphDB.refresh_schema()
        return {"result": self.graphDB.schema}
