/**
 * Backend HTTP client for the Chrome extension.
 */

const ApiClient = {
  BASE_URL: 'http://localhost:8000',

  async recipeDiff(ingredients, recipeTitle = null, recipeUrl = null) {
    const res = await fetch(`${this.BASE_URL}/api/recipes/diff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ingredients,
        recipe_title: recipeTitle,
        recipe_url: recipeUrl,
      }),
    });
    if (!res.ok) throw new Error(`Backend error: ${res.status}`);
    return res.json();
  },

  async listPantry() {
    const res = await fetch(`${this.BASE_URL}/api/pantry`);
    if (!res.ok) throw new Error(`Backend error: ${res.status}`);
    return res.json();
  },

  async addToPantry(item) {
    const res = await fetch(`${this.BASE_URL}/api/pantry`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item),
    });
    if (!res.ok) throw new Error(`Backend error: ${res.status}`);
    return res.json();
  },
};
