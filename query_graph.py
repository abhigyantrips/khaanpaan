from rdflib import Graph

# Load the knowledge graph
g = Graph()
g.parse("recipe_knowledge_graph.ttl", format="turtle")

print(f"Loaded graph with {len(g)} triples\n")

# Example SPARQL Queries

# Query 1: List all meals with their names
query1 = """
PREFIX recipe: <http://example.org/recipe/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?meal ?name
WHERE {
    ?meal a recipe:Meal ;
          recipe:hasName ?name .
}
LIMIT 10
"""

print("=== Query 1: List of Meals ===")
results = g.query(query1)
for row in results:
    print(f"  {row.name}")

# Query 2: Find meals by cuisine
query2 = """
PREFIX recipe: <http://example.org/recipe/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?mealName ?cuisineName
WHERE {
    ?meal a recipe:Meal ;
          recipe:hasName ?mealName ;
          recipe:belongsToCuisine ?cuisine .
    ?cuisine rdfs:label ?cuisineName .
    FILTER(?cuisineName = "Italian")
}
"""

print("\n=== Query 2: Italian Meals ===")
results = g.query(query2)
for row in results:
    print(f"  {row.mealName}")

# Query 3: List ingredients for a specific meal
query3 = """
PREFIX recipe: <http://example.org/recipe/>

SELECT ?ingredientName ?measure
WHERE {
    ?meal a recipe:Meal ;
          recipe:hasName ?mealName ;
          recipe:hasIngredient ?ingredient .
    ?ingredient recipe:ingredientName ?ingredientName ;
                recipe:ingredientMeasure ?measure .
}
LIMIT 20
"""

print("\n=== Query 3: Sample Ingredients ===")
results = g.query(query3)
for row in results:
    print(f"  {row.ingredientName}: {row.measure}")

# Query 4: Count meals by category
query4 = """
PREFIX recipe: <http://example.org/recipe/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?category (COUNT(?meal) as ?count)
WHERE {
    ?meal a recipe:Meal ;
          recipe:belongsToCategory ?cat .
    ?cat rdfs:label ?category .
}
GROUP BY ?category
ORDER BY DESC(?count)
"""

print("\n=== Query 4: Meals by Category ===")
results = g.query(query4)
for row in results:
    print(f"  {row.category}: {row.count} meals")

# Query 5: Find meals with specific ingredient
query5 = """
PREFIX recipe: <http://example.org/recipe/>

SELECT DISTINCT ?mealName
WHERE {
    ?meal a recipe:Meal ;
          recipe:hasName ?mealName ;
          recipe:hasIngredient ?ingredient .
    ?ingredient recipe:ingredientName ?ingredientName .
    FILTER(CONTAINS(LCASE(?ingredientName), "chicken"))
}
"""

print("\n=== Query 5: Meals with Chicken ===")
results = g.query(query5)
for row in results:
    print(f"  {row.mealName}")