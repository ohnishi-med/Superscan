// Superscan Background Service Worker
const POLLING_INTERVAL = 2000;

// Digikar Reception Page (The entry point for searching)
// const SEARCH_URL = 'https://digikar.jp/reception/'; 
const SEARCH_URL = 'http://127.0.0.1:8000/test/mock_emr.html?page=reception';
const KARTE_DOMAIN = '127.0.0.1'; // Switch back to local for mock verification

async function checkNewScan() {
    try {
        const response = await fetch('http://127.0.0.1:8000/check_new_scan');
        if (!response.ok) return;

        const data = await response.json();
        if (data.new_file) {
            console.log('New scan detected:', data);

            // 1. Store scan data for the content script to pick up after navigation
            await chrome.storage.local.set({
                pending_scan: {
                    patient_id: data.patient_id,
                    file_url: data.file_url,
                    filename: data.filename,
                    timestamp: Date.now()
                }
            });

            // 2. Perform Navigation (To Search Page)
            const targetUrl = SEARCH_URL;

            // Find EMR tab
            const allTabs = await chrome.tabs.query({});
            const emrTab = allTabs.find(t => t.url && t.url.includes(KARTE_DOMAIN));

            if (emrTab) {
                chrome.tabs.update(emrTab.id, { url: targetUrl, active: true });
            } else {
                chrome.tabs.create({ url: targetUrl });
            }

            // 3. Mark as processed in backend
            await fetch('http://127.0.0.1:8000/mark_processed', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: data.filename })
            });
        }
    } catch (error) {
        console.error('Polling error:', error);
    }
}

setInterval(checkNewScan, POLLING_INTERVAL);
