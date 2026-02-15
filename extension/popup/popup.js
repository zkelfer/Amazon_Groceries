/**
 * Popup script — queries content script for recipe, sends to backend for diff.
 */

const $loading = document.getElementById('loading');
const $noRecipe = document.getElementById('no-recipe');
const $error = document.getElementById('error');
const $results = document.getElementById('results');
const $title = document.getElementById('recipe-title');
const $summary = document.getElementById('summary');
const $list = document.getElementById('ingredient-list');

function showState(el) {
  [$loading, $noRecipe, $error, $results].forEach(s => s.classList.add('hidden'));
  el.classList.remove('hidden');
}

function esc(s) {
  const d = document.createElement('span');
  d.textContent = s;
  return d.innerHTML;
}

async function init() {
  showState($loading);

  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) {
      showState($noRecipe);
      return;
    }

    // Ask content script for recipe
    const response = await chrome.tabs.sendMessage(tab.id, { type: 'GET_RECIPE' });

    if (!response?.recipe || !response.recipe.ingredients?.length) {
      showState($noRecipe);
      return;
    }

    const recipe = response.recipe;

    // Send to backend for diff
    const diff = await ApiClient.recipeDiff(
      recipe.ingredients,
      recipe.title,
      recipe.url
    );

    // Render results
    $title.textContent = diff.recipe_title || 'Recipe';
    $summary.textContent = `${diff.in_pantry_count} in pantry · ${diff.missing_count} missing`;

    $list.innerHTML = diff.ingredients.map(ing => {
      const badge = ing.in_pantry
        ? '<span class="badge badge-ok">Have</span>'
        : '<span class="badge badge-miss">Need</span>';

      let details = `<span class="ing-name">${esc(ing.raw)}</span>`;
      if (ing.in_pantry && ing.pantry_match) {
        details += `<span class="ing-match">(matched: ${esc(ing.pantry_match)})</span>`;
      }
      if (ing.whole_foods_url) {
        try {
          const url = new URL(ing.whole_foods_url);
          if (['http:', 'https:'].includes(url.protocol)) {
            details += `<a class="ing-link" href="${esc(ing.whole_foods_url)}" target="_blank" rel="noopener">Buy on Whole Foods →</a>`;
          }
        } catch (e) {
          // skip invalid URLs
        }
      }

      return `<li>${badge}<div class="ing-details">${details}</div></li>`;
    }).join('');

    showState($results);

  } catch (err) {
    const msg = document.querySelector('.error-msg');
    msg.textContent = err.message || 'Failed to connect to backend';
    showState($error);
  }
}

init();
