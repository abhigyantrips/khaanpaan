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
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

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


def visualize_knowledge_graph(rdf_graph, output_file="recipe_kg_visualization.png"):
    """Generate and export a visualization of the knowledge graph."""
    print("\nGenerating knowledge graph visualization...")
    
    # Create NetworkX graph
    nx_graph = nx.DiGraph()
    
    # Track node types for coloring
    node_types = defaultdict(set)
    node_labels = {}
    
    # Add nodes and edges from RDF graph
    for subj, pred, obj in rdf_graph:
        subj_str = str(subj)
        pred_str = str(pred).split("/")[-1].split("#")[-1]
        obj_str = str(obj)
        
        # Determine node types
        if str(MEAL) in subj_str:
            node_types['meal'].add(subj_str)
        elif str(CATEGORY) in subj_str:
            node_types['category'].add(subj_str)
        elif str(CUISINE) in subj_str:
            node_types['cuisine'].add(subj_str)
        elif str(INGREDIENT) in subj_str:
            node_types['ingredient'].add(subj_str)
        
        # Skip RDF.type and RDFS predicates
        if pred in [RDF.type, RDFS.label]:
            continue
        
        # Skip literal objects for cleaner visualization
        if isinstance(obj, Literal):
            # Store labels for display
            if pred_str in ['hasName', 'label', 'ingredientName']:
                node_labels[subj_str] = str(obj)[:20]
            continue
        
        # Add edge only if both nodes will be in the graph
        if str(CATEGORY) in obj_str:
            node_types['category'].add(obj_str)
        elif str(CUISINE) in obj_str:
            node_types['cuisine'].add(obj_str)
        elif str(INGREDIENT) in obj_str:
            node_types['ingredient'].add(obj_str)
        elif str(MEAL) in obj_str:
            node_types['meal'].add(obj_str)
        else:
            # Skip objects that aren't our entity types
            continue
        
        # Add edge
        nx_graph.add_edge(subj_str, obj_str, label=pred_str)
    
    # Set up visualization
    plt.figure(figsize=(20, 16))
    
    # Use shell_layout (doesn't require scipy)
    # Organize nodes in shells by type
    shells = [
        list(node_types.get('cuisine', [])),
        list(node_types.get('category', [])),
        list(node_types.get('meal', [])),
        list(node_types.get('ingredient', []))
    ]
    shells = [shell for shell in shells if shell]  # Remove empty shells
    
    try:
        pos = nx.shell_layout(nx_graph, nlist=shells)
    except:
        # Fallback to circular layout if shell fails
        pos = nx.circular_layout(nx_graph)
    
    # Define colors for different node types
    colors = {
        'meal': '#FF6B6B',
        'category': '#4ECDC4',
        'cuisine': '#45B7D1',
        'ingredient': '#FFA07A',
        'default': '#95E1D3'
    }
    
    # Draw nodes by type
    for node_type, nodes in node_types.items():
        nx.draw_networkx_nodes(
            nx_graph,
            pos,
            nodelist=list(nodes),
            node_color=colors.get(node_type, colors['default']),
            node_size=500 if node_type in ['category', 'cuisine'] else 100,
            alpha=0.8,
            label=node_type.capitalize()
        )
    
    # Draw edges
    nx.draw_networkx_edges(
        nx_graph,
        pos,
        edge_color='gray',
        arrows=True,
        arrowsize=10,
        alpha=0.3,
        width=0.5
    )
    
    # Add labels for category and cuisine nodes
    label_nodes = {
        node: node_labels.get(node, node.split("/")[-1][:15])
        for node in list(node_types.get('category', [])) + list(node_types.get('cuisine', []))
    }
    nx.draw_networkx_labels(
        nx_graph,
        pos,
        labels=label_nodes,
        font_size=8,
        font_weight='bold'
    )
    
    plt.title(
        "Recipe Knowledge Graph Visualization\n"
        f"Nodes: {nx_graph.number_of_nodes()} | "
        f"Edges: {nx_graph.number_of_edges()}",
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, loc='upper left')
    plt.axis('off')
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Visualization saved: {output_file}")
    plt.close()

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
    
    # Generate visualization
    visualize_knowledge_graph(g, "recipe_knowledge_graph.png")
    
    print("\nAll files exported successfully!")


if __name__ == "__main__":
    main()