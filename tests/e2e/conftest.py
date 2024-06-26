#  Copyright (c) "Neo4j"
#  Neo4j Sweden AB [https://neo4j.com]
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      https://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import string
import random
import uuid

import pytest
from neo4j import GraphDatabase
from neo4j_genai.embedder import Embedder
from neo4j_genai.indexes import drop_index, create_vector_index, create_fulltext_index


@pytest.fixture(scope="module")
def driver():
    uri = "neo4j://localhost:7687"
    auth = ("neo4j", "password")
    driver = GraphDatabase.driver(uri, auth=auth)
    yield driver
    driver.close()


@pytest.fixture(scope="module")
def custom_embedder():
    class CustomEmbedder(Embedder):
        def embed_query(self, text: str) -> list[float]:
            return [random.random() for _ in range(1536)]

    return CustomEmbedder()


@pytest.fixture(scope="module")
def setup_neo4j(driver):
    vector_index_name = "vector-index-name"
    fulltext_index_name = "fulltext-index-name"

    # Delete data and drop indexes to prevent data leakage
    driver.execute_query("MATCH (n) DETACH DELETE n")
    drop_index(driver, vector_index_name)
    drop_index(driver, fulltext_index_name)

    # Create a vector index
    create_vector_index(
        driver,
        vector_index_name,
        label="Document",
        property="propertyKey",
        dimensions=1536,
        similarity_fn="euclidean",
    )

    # Create a fulltext index
    create_fulltext_index(
        driver, fulltext_index_name, label="Document", node_properties=["propertyKey"]
    )

    # Insert 10 vectors and authors
    vector = [random.random() for _ in range(1536)]

    def random_str(n: int) -> str:
        return "".join([random.choice(string.ascii_letters) for _ in range(n)])

    for i in range(10):
        insert_query = (
            "MERGE (doc:Document {id: $id})"
            "WITH doc "
            "CALL db.create.setNodeVectorProperty(doc, 'propertyKey', $vector)"
            "WITH doc "
            "MERGE (author:Author {name: $authorName})"
            "MERGE (doc)-[:AUTHORED_BY]->(author)"
            "RETURN doc, author"
        )

        parameters = {
            "id": str(uuid.uuid4()),
            "vector": vector,
            "authorName": random_str(10),
        }
        driver.execute_query(insert_query, parameters)
