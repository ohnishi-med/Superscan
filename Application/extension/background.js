// Background Service Worker
// Polls the Python backend for new scan data.

const POLLING_INTERVAL_MS = 1000;
const SERVER_URL = "http://127.0.0.1:8000";

async function pollServer() {
  try {
    const response = await fetch(`${SERVER_URL}/check_new_scan`);
    if (!response.ok) return;

    const data = await response.json();
    if (data && data.patient_id) {
      console.log("New scan detected:", data);
      await processScanData(data);
    }
  } catch (err) {
    // console.error("Polling error:", err); // Suppress log to avoid spam
  }
}

async function processScanData(scanData) {
    // 1. Mark as processed immediately to prevent double processing? 
    // Or wait until success? Let's mark it process after dispatching to content script.
    
    // 2. Find active tab or create new one?
    // User Assumption: "Current tab (or new tab) is updated"
    // We will try to get the active tab in the current window.
    
    const [activeTab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    
    if (activeTab) {
        // Send message to content script to handle navigation
        // Note: We can't easily navigate FROM background if we want to ensure the content script 
        // handles the specific URL pattern logic which is defined in content_script.js (User Requirement).
        // However, we can't inject config into background easy without duplicating it.
        // STRATEGY: Send data to content script, let content script decide URL.
        // BUT: If the current page is NOT the target domain, content script might need to redirect.
        
        try {
            await chrome.tabs.sendMessage(activeTab.id, {
                type: "NEW_SCAN",
                data: scanData
            });
            
            // Mark processed in backend
            await fetch(`${SERVER_URL}/mark_processed`, { method: "POST" });
            
        } catch (e) {
            console.error("Failed to send message to content script:", e);
        }
    }
}

// Start polling
setInterval(pollServer, POLLING_INTERVAL_MS);
