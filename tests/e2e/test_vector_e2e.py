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

import pytest

from neo4j import Record

from neo4j_genai import VectorRetriever, VectorCypherRetriever
from neo4j_genai.types import VectorSearchRecord


@pytest.mark.usefixtures("setup_neo4j")
def test_vector_retriever_search_text(driver, custom_embedder):
    retriever = VectorRetriever(driver, "vector-index-name", custom_embedder)

    top_k = 5
    results = retriever.search(query_text="Find me a book about Fremen", top_k=top_k)

    assert isinstance(results, list)
    assert len(results) == 5
    for result in results:
        assert isinstance(result, VectorSearchRecord)


@pytest.mark.usefixtures("setup_neo4j")
def test_vector_cypher_retriever_search_text(driver, custom_embedder):
    retrieval_query = (
        "MATCH (node)-[:AUTHORED_BY]->(author:Author) " "RETURN author.name"
    )
    retriever = VectorCypherRetriever(
        driver, "vector-index-name", retrieval_query, custom_embedder
    )

    top_k = 5
    results = retriever.search(query_text="Find me a book about Fremen", top_k=top_k)

    assert isinstance(results, list)
    assert len(results) == 5
    for record in results:
        assert isinstance(record, Record)
        assert "author.name" in record.keys()


@pytest.mark.usefixtures("setup_neo4j")
def test_vector_retriever_search_vector(driver):
    retriever = VectorRetriever(driver, "vector-index-name")

    top_k = 5
    results = retriever.search(query_vector=[1.0 for _ in range(1536)], top_k=top_k)

    assert isinstance(results, list)
    assert len(results) == 5
    for result in results:
        assert isinstance(result, VectorSearchRecord)


@pytest.mark.usefixtures("setup_neo4j")
def test_vector_cypher_retriever_search_vector(driver):
    retrieval_query = (
        "MATCH (node)-[:AUTHORED_BY]->(author:Author) " "RETURN author.name"
    )
    retriever = VectorCypherRetriever(driver, "vector-index-name", retrieval_query)

    top_k = 5
    results = retriever.search(query_vector=[1.0 for _ in range(1536)], top_k=top_k)

    assert isinstance(results, list)
    assert len(results) == 5
    for record in results:
        assert isinstance(record, Record)
        assert "author.name" in record.keys()


@pytest.mark.usefixtures("setup_neo4j")
def test_vector_retriever_return_properties(driver):
    properties = ["name", "age"]
    retriever = VectorRetriever(
        driver,
        "vector-index-name",
        return_properties=properties,
    )

    top_k = 5
    results = retriever.search(
        query_vector=[1.0 for _ in range(1536)],
        top_k=top_k,
    )

    assert isinstance(results, list)
    assert len(results) == 5
    for result in results:
        assert isinstance(result, VectorSearchRecord)
