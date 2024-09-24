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

    def populate_data(self):
        query = """
        LOAD CSV WITH HEADERS FROM 
        'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv'
        AS row
        MERGE (m:Movie {id:row.movieId})
        SET m.released = date(row.released),
            m.title = row.title,
            m.imdbRating = toFloat(row.imdbRating)
        FOREACH (director in split(row.director, '|') | 
            MERGE (p:Person {name:trim(director)})
            MERGE (p)-[:DIRECTED]->(m))
        FOREACH (actor in split(row.actors, '|') | 
            MERGE (p:Person {name:trim(actor)})
            MERGE (p)-[:ACTED_IN]->(m))
        FOREACH (genre in split(row.genres, '|') | 
            MERGE (g:Genre {name:trim(genre)})
            MERGE (m)-[:IN_GENRE]->(g))
        """
        self.graphDB.query(query)
        self.graphDB.refresh_schema()
        return {"result": self.graphDB.schema}
