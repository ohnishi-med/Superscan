// Superscan Content Script
console.log('Superscan Extension Active on Digikar');

// 1. Check for pending actions on load
chrome.storage.local.get(['pending_scan'], (result) => {
    if (result.pending_scan) {
        const scan = result.pending_scan;
        if (Date.now() - scan.timestamp < 60000) {
            console.log('Picking up pending scan:', scan);
            executeScanAction(scan);
        }
    }
});

async function executeScanAction(data) {
    const { patient_id } = data;
    const currentUrl = window.location.href;

    // STEP 1: If on Reception Page -> Handle Search & Open Chart
    if (currentUrl.includes('/reception/')) {
        await handleSearchFlow(patient_id);
    }
    // STEP 2: If on Patient Chart Page -> Handle File Tab & Add Button
    else if (currentUrl.includes('/karte/patients/')) {
        const success = await handleChartFlow(data);
        if (success) {
            // Flow complete: Clear the pending scan
            chrome.storage.local.remove(['pending_scan']);
            console.log('Superscan Flow Complete');
        }
    }
}

async function handleSearchFlow(patient_id) {
    let searchInput = document.querySelector('input[placeholder*="患者番号"]');

    if (!searchInput) {
        const searchBtn = document.querySelector('button.css-1nnxsgs');
        if (searchBtn) {
            searchBtn.click();
            await new Promise(resolve => setTimeout(resolve, 600)); // Slightly longer wait for DOM
            searchInput = document.querySelector('input[placeholder*="患者番号"]');
        }
    }

    if (searchInput) {
        searchInput.value = patient_id || '';
        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
        searchInput.dispatchEvent(new Event('change', { bubbles: true }));
        searchInput.style.backgroundColor = '#e8f0fe';
        showNotification(`Superscan: ID ${patient_id} を検索中...`);

        // Trigger Search
        setTimeout(() => {
            searchInput.dispatchEvent(new KeyboardEvent('keydown', {
                bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
            }));

            // Wait for results
            const observer = new MutationObserver((mutations, obs) => {
                const showLink = document.querySelector('a[target="_blank"][href*="/karte/patients/"]');
                if (showLink) {
                    showNotification(`Superscan: 患者が見つかりました。新しいタブでカルテを開きます...`);
                    showLink.click();
                    obs.disconnect();
                    // We DON'T clear storage here because we need it in the newly opened tab
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
            setTimeout(() => observer.disconnect(), 6000);
        }, 500);
    }
}

async function handleChartFlow(data) {
    const { patient_id, file_url } = data;
    const tabs = Array.from(document.querySelectorAll('li, span, a'));
    const fileTab = tabs.find(el => el.textContent.trim() === 'ファイル');

    if (fileTab) {
        showNotification('Superscan: ファイルタブを表示します...');
        fileTab.click();
        await new Promise(resolve => setTimeout(resolve, 800));

        // 2. Click the "Add Attachment" button
        const buttons = Array.from(document.querySelectorAll('button'));
        let addBtn = buttons.find(b => b.textContent.includes('作成') || b.textContent.includes('追加'));

        if (addBtn) {
            showNotification('Superscan: アップロード画面を開いています...');
            addBtn.click();
            await new Promise(resolve => setTimeout(resolve, 800));

            // 3. Automated File Selection
            const fileInput = document.querySelector('input[type="file"]');
            if (fileInput && file_url) {
                try {
                    // Fetch the scanned image and create a File object
                    const response = await fetch(file_url);
                    const blob = await response.blob();
                    const file = new File([blob], "superscan_capture.jpg", { type: "image/jpeg" });

                    // Use DataTransfer to set the file input (Security-compliant way to simulate drop)
                    const container = new DataTransfer();
                    container.items.add(file);
                    fileInput.files = container.files;
                    fileInput.dispatchEvent(new Event('change', { bubbles: true }));

                    showNotification('Superscan: ファイルを自動選択しました。', 'info');
                    await new Promise(resolve => setTimeout(resolve, 500));

                    // 4. Click the final "Add" (追加) button in the modal
                    // Looking for the green button in the modal
                    const modalButtons = Array.from(document.querySelectorAll('div[role="dialog"] button, .upload-modal button, button'));
                    const finalSubmitBtn = modalButtons.find(b => b.textContent === '追加' && b !== addBtn);

                    if (finalSubmitBtn) {
                        finalSubmitBtn.click();
                        // Final Completion Message
                        const docType = "診療情報提供書"; // This would come from AI in production
                        showNotification(`完了：ID ${patient_id} ${docType} を追加しました`, 'success');
                        return true;
                    }
                } catch (e) {
                    console.error('Superscan Upload Error:', e);
                    showNotification('Superscan: ファイルの自動添付に失敗しました', 'warning');
                }
            }
        }
    }
    return false;
}

function showNotification(text, type = 'info') {
    let div = document.getElementById('superscan-notify');
    if (!div) {
        div = document.createElement('div');
        div.id = 'superscan-notify';
        div.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 25px;
      border-radius: 8px;
      z-index: 999999;
      color: white;
      font-family: sans-serif;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      transition: opacity 0.3s ease;
      font-weight: bold;
    `;
        document.body.appendChild(div);
    }

    if (type === 'success') div.style.backgroundColor = '#4CAF50';
    else if (type === 'warning') div.style.backgroundColor = '#FF9800';
    else div.style.backgroundColor = '#2196F3';

    div.innerText = text;
    div.style.opacity = '1';

    setTimeout(() => {
        div.style.opacity = '0';
    }, 5000);
}
