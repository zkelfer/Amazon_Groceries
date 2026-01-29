/**
 * Recipe extraction strategies.
 * Tries JSON-LD (schema.org/Recipe) first, then falls back to DOM scraping.
 */

const RecipeExtractors = {
  /**
   * Extract recipe data from JSON-LD structured data (schema.org/Recipe).
   * Most major recipe sites embed this for SEO.
   */
  extractJsonLd() {
    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
    for (const script of scripts) {
      try {
        let data = JSON.parse(script.textContent);

        // Handle @graph arrays
        if (data['@graph']) {
          data = data['@graph'];
        }

        // Normalize to array
        const items = Array.isArray(data) ? data : [data];

        for (const item of items) {
          if (item['@type'] === 'Recipe' ||
              (Array.isArray(item['@type']) && item['@type'].includes('Recipe'))) {
            return {
              title: item.name || '',
              ingredients: (item.recipeIngredient || []).map(s => s.trim()),
              url: window.location.href,
              source: 'json-ld',
            };
          }
        }
      } catch (e) {
        // Invalid JSON, skip
      }
    }
    return null;
  },

  /**
   * DOM-based extraction fallback.
   * Looks for common ingredient list patterns across recipe sites.
   */
  extractDom() {
    const selectors = [
      // Common ingredient list selectors
      '.recipe-ingredients li',
      '.ingredients-section li',
      '[class*="ingredient"] li',
      '.mntl-structured-ingredients__list-item',  // allrecipes
      '.o-Ingredients__a-Ingredient',               // food network
      '.recipe-ingredients__list-item',
      'ul.recipe-ingredients li',
      '[data-testid="ingredient-list"] li',
      '.ingredient-list li',
      '.ingredients li',
      // Generic fallback
      '[itemprop="recipeIngredient"]',
    ];

    for (const selector of selectors) {
      const elements = document.querySelectorAll(selector);
      if (elements.length > 0) {
        const ingredients = Array.from(elements)
          .map(el => el.textContent.trim())
          .filter(text => text.length > 0 && text.length < 200);

        if (ingredients.length >= 2) {
          const titleEl = document.querySelector('h1') || document.querySelector('.recipe-title');
          return {
            title: titleEl ? titleEl.textContent.trim() : document.title,
            ingredients,
            url: window.location.href,
            source: 'dom',
          };
        }
      }
    }
    return null;
  },

  /**
   * Try all extraction strategies in order.
   */
  extract() {
    return this.extractJsonLd() || this.extractDom() || null;
  },
};

// Make available globally for content script
if (typeof window !== 'undefined') {
  window.RecipeExtractors = RecipeExtractors;
}
