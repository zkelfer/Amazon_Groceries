/**
 * Background service worker.
 * Updates badge when recipe is found on current tab.
 */

chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg.type === 'RECIPE_FOUND' && sender.tab) {
    chrome.action.setBadgeText({ tabId: sender.tab.id, text: '✓' });
    chrome.action.setBadgeBackgroundColor({ tabId: sender.tab.id, color: '#4CAF50' });
  }
});
