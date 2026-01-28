// CONFIGURATION OBJECT - USER EDITABLE
// ユーザーはこのオブジェクトを編集してカルテ環境に合わせます。
const KARTE_CONFIG = {
  // URL pattern: {{id}} will be replaced by patient_id
  // Example: "https://example-karte.com/patients/{{id}}/files"
  targetUrlPattern: "https://example-karte.com/patients/{{id}}/files",
  
  // CSS Selector for the upload dropzone or file input
  // Example: "div.file-upload-area" or "input[type='file']"
  dropZoneSelector: "div.file-upload-area", 
  
  // If specific button needs to be clicked after drop (Optional)
  submitButtonSelector: "button#upload-confirm"
};

// --- Logic ---

console.log("Superscan Content Script Loaded");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "NEW_SCAN") {
    handleNewScan(message.data);
  }
});

async function handleNewScan(data) {
  const patientId = data.patient_id;
  const imageB64 = data.image_b64;

  const targetUrl = KARTE_CONFIG.targetUrlPattern.replace("{{id}}", patientId);
  
  // Check if we are on the correct page
  if (window.location.href !== targetUrl) {
    console.log(`Navigating to ${targetUrl}...`);
    // Store data in sessionStorage so we can access it after reload
    sessionStorage.setItem("pending_upload_image", imageB64);
    sessionStorage.setItem("pending_upload_patient", patientId);
    window.location.href = targetUrl;
  } else {
    // Already on page, just upload
    console.log("Already on target page, processing upload...");
    await performFileUpload(imageB64);
  }
}

// Check on load if we have pending upload
window.addEventListener("load", async () => {
    const pendingImage = sessionStorage.getItem("pending_upload_image");
    if (pendingImage) {
        console.log("Found pending upload from session.");
        sessionStorage.removeItem("pending_upload_image"); // Clear
        sessionStorage.removeItem("pending_upload_patient");
        
        // Wait a bit for dynamic elements to load
        setTimeout(() => performFileUpload(pendingImage), 1500); 
    }
});

function dataURLtoFile(dataurl, filename) {
    var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
}

async function performFileUpload(base64Image) {
    const dropZone = document.querySelector(KARTE_CONFIG.dropZoneSelector);
    if (!dropZone) {
        console.error(`Drop zone not found: ${KARTE_CONFIG.dropZoneSelector}`);
        alert(`Superscan Error: Drop zone not found (${KARTE_CONFIG.dropZoneSelector})`);
        return;
    }

    const file = dataURLtoFile(base64Image, "scanned_document.jpg");
    
    // Check if it's an input[type='file'] or a div
    if (dropZone.tagName === 'INPUT' && dropZone.type === 'file') {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        dropZone.files = dataTransfer.files;
        dropZone.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
        // Drag and Drop simulation
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        
        const dragEventDict = {
            bubbles: true,
            cancelable: true,
            composed: true,
            dataTransfer: dataTransfer
        };

        dropZone.dispatchEvent(new DragEvent('dragenter', dragEventDict));
        dropZone.dispatchEvent(new DragEvent('dragover', dragEventDict));
        dropZone.dispatchEvent(new DragEvent('drop', dragEventDict));
    }
    
    console.log("File drop event dispatched.");
    
    // Optional Submit
    if (KARTE_CONFIG.submitButtonSelector) {
        const submitBtn = document.querySelector(KARTE_CONFIG.submitButtonSelector);
        if (submitBtn) {
            setTimeout(() => submitBtn.click(), 500);
        }
    }
}
