import pandas as pd
import glob
import zipfile
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Path to ZIP file
zip_path = 'data/archive.zip'  # Adjust path to your ZIP file

# Extract ZIP file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall('archive')  # Folder to extract files

# Get all CSV files after extraction
csv_files = glob.glob('archive/*.csv')

# Read and combine all CSV files into a single DataFrame
df_list = [pd.read_csv(file) for file in csv_files]
indonesia_food_dataset = pd.concat(df_list, ignore_index=True)

# Remove duplicates based on the 'Title' column
indonesia_food_dataset = indonesia_food_dataset.drop_duplicates(subset='Title')

# Replace NaN with empty strings in 'Ingredients' column
indonesia_food_dataset['Ingredients'] = indonesia_food_dataset['Ingredients'].fillna('')

# TF-IDF Vectorizer for the 'Ingredients' column
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(indonesia_food_dataset['Ingredients'])

def recommend_by_ingredients(ingredients_input):
    input_str = " ".join(ingredients_input)
    input_tfidf = tfidf.transform([input_str])
    sim_scores = cosine_similarity(input_tfidf, tfidf_matrix).flatten()
    
    sim_scores = list(enumerate(sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    sim_scores = sim_scores[:5]
    recipe_indices = [i[0] for i in sim_scores if i[1] > 0]

    if not recipe_indices:
        return []

    recommended_recipes = indonesia_food_dataset[['Title', 'Ingredients', 'Steps']].iloc[recipe_indices]

    output = []
    for _, row in recommended_recipes.iterrows():
        steps = [step.strip() for step in row['Steps'].split('--') if step.strip()]
        numbered_steps = [f"{i + 1}. {step}" for i, step in enumerate(steps)]
        steps_formatted = "\n".join(numbered_steps)

        ingredients_list = [ingredient.strip() for ingredient in row['Ingredients'].split('--') if ingredient.strip()]
        numbered_ingredients = [f"{i + 1}. {ingredient}" for i, ingredient in enumerate(ingredients_list)]
        ingredients_formatted = "\n".join(numbered_ingredients)

        output.append({
            'Title': row['Title'],
            'Ingredients': ingredients_formatted,
            'Steps': steps_formatted
        })

    return output
