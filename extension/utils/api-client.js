/**
 * Backend HTTP client for the Chrome extension.
 */

const ApiClient = {
  BASE_URL: (() => {
    const stored = typeof chrome !== 'undefined' && chrome.storage
      ? null  // will be overridden at runtime
      : null;
    // Default to localhost for development; configurable via setBaseUrl()
    return 'http://localhost:8000';
  })(),

  setBaseUrl(url) {
    // Enforce HTTPS for non-localhost backends
    const parsed = new URL(url);
    if (!['localhost', '127.0.0.1'].includes(parsed.hostname) && parsed.protocol !== 'https:') {
      parsed.protocol = 'https:';
    }
    this.BASE_URL = parsed.origin;
  },

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
