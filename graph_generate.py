"""
RDFS Recipe Knowledge Graph Generator

This script fetches recipe data from TheMealDB API and generates
an RDF knowledge graph.

Data Source: TheMealDB (https://www.themealdb.com)
API: https://www.themealdb.com/api.php
License: Free for non-commercial use with attribution

Author: Abhigyan Tripathi
Date: October 2025
"""

import requests
import time
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from urllib.parse import quote

# Define namespaces
RECIPE = Namespace("http://example.org/recipe/")
MEAL = Namespace("http://example.org/meal/")
INGREDIENT = Namespace("http://example.org/ingredient/")
CATEGORY = Namespace("http://example.org/category/")
CUISINE = Namespace("http://example.org/cuisine/")

# Initialize graph
g = Graph()
g.bind("recipe", RECIPE)
g.bind("meal", MEAL)
g.bind("ingredient", INGREDIENT)
g.bind("category", CATEGORY)
g.bind("cuisine", CUISINE)


def fetch_random_meals(count=50):
    """Fetch random meals from TheMealDB API."""
    meals = []
    print(f"Fetching {count} meals from TheMealDB API...")
    
    for i in range(count):
        try:
            response = requests.get(
                "https://www.themealdb.com/api/json/v1/1/random.php"
            )
            if response.status_code == 200:
                meal = response.json()["meals"][0]
                meals.append(meal)
                print(f"Fetched: {meal['strMeal']} ({i+1}/{count})")
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"Error fetching meal {i+1}: {e}")
    
    return meals


def create_uri_ref(namespace, value):
    """Create a safe URI reference."""
    if value:
        safe_value = quote(value.strip().replace(" ", "_"))
        return namespace[safe_value]
    return None


def add_meal_to_graph(meal):
    """Add a meal and its properties to the RDF graph."""
    meal_id = meal["idMeal"]
    meal_uri = MEAL[meal_id]
    
    # Add meal as instance of Meal class
    g.add((meal_uri, RDF.type, RECIPE.Meal))
    
    # Add basic properties
    if meal.get("strMeal"):
        g.add((meal_uri, RECIPE.hasName, Literal(meal["strMeal"])))
    
    if meal.get("strInstructions"):
        g.add((meal_uri, RECIPE.hasInstructions, 
               Literal(meal["strInstructions"])))
    
    if meal.get("strMealThumb"):
        g.add((meal_uri, RECIPE.hasThumbnail, Literal(meal["strMealThumb"])))
    
    if meal.get("strYoutube"):
        g.add((meal_uri, RECIPE.hasYoutubeLink, Literal(meal["strYoutube"])))
    
    # Add category
    if meal.get("strCategory"):
        category_uri = create_uri_ref(CATEGORY, meal["strCategory"])
        g.add((category_uri, RDF.type, RECIPE.Category))
        g.add((category_uri, RDFS.label, Literal(meal["strCategory"])))
        g.add((meal_uri, RECIPE.belongsToCategory, category_uri))
    
    # Add cuisine/area
    if meal.get("strArea"):
        cuisine_uri = create_uri_ref(CUISINE, meal["strArea"])
        g.add((cuisine_uri, RDF.type, RECIPE.Cuisine))
        g.add((cuisine_uri, RDFS.label, Literal(meal["strArea"])))
        g.add((meal_uri, RECIPE.belongsToCuisine, cuisine_uri))
    
    # Add ingredients
    for i in range(1, 21):
        ingredient_name = meal.get(f"strIngredient{i}")
        ingredient_measure = meal.get(f"strMeasure{i}")
        
        if ingredient_name and ingredient_name.strip():
            ingredient_uri = URIRef(
                f"{INGREDIENT}{meal_id}_ingredient_{i}"
            )
            
            g.add((ingredient_uri, RDF.type, RECIPE.Ingredient))
            g.add((ingredient_uri, RECIPE.ingredientName, 
                   Literal(ingredient_name.strip())))
            
            if ingredient_measure and ingredient_measure.strip():
                g.add((ingredient_uri, RECIPE.ingredientMeasure, 
                       Literal(ingredient_measure.strip())))
            
            g.add((meal_uri, RECIPE.hasIngredient, ingredient_uri))


def main():
    print("=== RDFS Recipe Knowledge Graph Generator ===\n")
    
    # Fetch meals
    meals = fetch_random_meals(count=50)
    
    print(f"\n{len(meals)} meals fetched. Building knowledge graph...\n")
    
    # Add meals to graph
    for meal in meals:
        add_meal_to_graph(meal)
    
    # Serialize to Turtle file
    output_file = "recipe_knowledge_graph.ttl"
    g.serialize(destination=output_file, format="turtle")
    
    print(f"\nKnowledge graph generated successfully!")
    print(f"Output: {output_file}")
    print(f"Total triples: {len(g)}")


if __name__ == "__main__":
    main()