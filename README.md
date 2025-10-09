# RDFS Recipe Knowledge Graph

An RDFS-based knowledge graph of recipes from TheMealDB API, queryable with SPARQL.

## Overview

This project constructs a semantic knowledge graph representing recipe information including meals, ingredients, cuisines, and categories using RDF/RDFS.

## Schema

The RDFS schema defines:
- **Classes**: `Meal`, `Ingredient`, `Category`, `Cuisine`
- **Properties**: `hasName`, `hasIngredient`, `belongsToCategory`, `belongsToCuisine`, etc.

## Installation

```bash
pip install rdflib requests
```

## Usage

### Generate Knowledge Graph
```bash
python graph_generate.py
```
This fetches 50 random meals from TheMealDB and creates `recipe_knowledge_graph.ttl`.

### Query the Graph
```bash
python graph_query.py
```
Runs example SPARQL queries against the generated graph.

## Example SPARQL Queries

### List all meals
```sparql
PREFIX recipe: <http://example.org/recipe/>
SELECT ?meal ?name WHERE {
    ?meal a recipe:Meal ; recipe:hasName ?name .
}
```

### Find Italian meals
```sparql
PREFIX recipe: <http://example.org/recipe/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?mealName WHERE {
    ?meal recipe:hasName ?mealName ;
          recipe:belongsToCuisine ?cuisine .
    ?cuisine rdfs:label "Italian" .
}
```

## File Structure

```
├── graph_generate.py          # Graph generation script
├── graph_query.py             # SPARQL query examples
├── schema.ttl                 # RDFS schema definition
├── recipe_knowledge_graph.ttl # Generated knowledge graph
└── README.md                  # Documentation
```

## Attribution

This project uses data from **TheMealDB**, an open recipe database.

- **Website**: [https://www.themealdb.com](https://www.themealdb.com)
- **API Documentation**: [https://www.themealdb.com/api.php](https://www.themealdb.com/api.php)
- **License**: TheMealDB API is free to use for non-commercial purposes with attribution

### TheMealDB License Terms
If you use TheMealDB data, please:
- Provide attribution to TheMealDB
- Link back to their website
- Not use for commercial purposes without a commercial license

For commercial use, visit: [https://www.themealdb.com/api.php](https://www.themealdb.com/api.php).

## License

MIT License. See `LICENSE` file for details.