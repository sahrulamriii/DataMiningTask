from flask import Flask, render_template, request
import requests
from recommendation_model import recommend_by_ingredients

app = Flask(__name__)

access_key = '3m6H08RYv2KbFdFVMUef1USp5JSi_qCZ_gDic2mTFhw'  # Unsplash Access Key

def get_unsplash_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={access_key}&count=1"
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses

        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['urls']['regular']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
    
    return "https://via.placeholder.com/150"  # Fallback image

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get ingredients input from the form
        ingredients_input = [request.form.get("ingredient1"), 
                             request.form.get("ingredient2"), 
                             request.form.get("ingredient3")]
        
        # Call recommendation function
        recommendations = recommend_by_ingredients(ingredients_input)
        
        # Add image URLs to recommendations
        for recipe in recommendations:
            recipe['image_url'] = get_unsplash_image(recipe['Title'])
        
        return render_template("index.html", recommendations=recommendations)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
