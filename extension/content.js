/**
 * Content script — runs on recipe pages.
 * Extracts ingredients on load and responds to popup messages.
 */

let cachedRecipe = null;

function extractRecipe() {
  if (!cachedRecipe) {
    cachedRecipe = RecipeExtractors.extract();
  }
  return cachedRecipe;
}

// Extract on load
extractRecipe();

// Respond to popup requests
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'GET_RECIPE') {
    const recipe = extractRecipe();
    sendResponse({ recipe });
  }
  return true; // keep channel open for async response
});
