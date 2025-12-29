const API_URL = "http://localhost:8000";

let selectedFile = null;

// Check Authentication
function checkAuth() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "index.html";
    return false;
  }
  return token;
}

// Initialize Theme
function initTheme() {
  const theme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", theme);

  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
}

// Initialize Analysis Page
function initAnalysisPage() {
  checkAuth();
  setupFileUpload();
  setupPatientForm();
  updateUserInfo();
}

// Update User Info
function updateUserInfo() {
  const doctorName = localStorage.getItem("doctorName");
  const userNameEl = document.querySelector(".user-info h4");
  const userAvatarEl = document.querySelector(".user-avatar");

  if (userNameEl) userNameEl.textContent = doctorName || "Doctor";
  if (userAvatarEl && doctorName) {
    userAvatarEl.textContent = doctorName.charAt(0).toUpperCase();
  }
}

// Setup File Upload
function setupFileUpload() {
  const uploadArea = document.getElementById("uploadArea");
  const fileInput = document.getElementById("fileInput");
  const imagePreview = document.getElementById("imagePreview");
  const previewImage = document.getElementById("previewImage");
  const removeImageBtn = document.getElementById("removeImage");

  if (!uploadArea || !fileInput) return;

  // Click to upload
  uploadArea.addEventListener("click", () => {
    fileInput.click();
  });

  // File selection
  fileInput.addEventListener("change", (e) => {
    handleFileSelect(e.target.files[0]);
  });

  // Drag and drop
  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.classList.add("dragover");
  });

  uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("dragover");
  });

  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("dragover");
    handleFileSelect(e.dataTransfer.files[0]);
  });

  // Remove image
  if (removeImageBtn) {
    removeImageBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      selectedFile = null;
      fileInput.value = "";
      imagePreview.classList.remove("active");
    });
  }
}

// Handle File Selection
function handleFileSelect(file) {
  if (!file) return;

  if (!file.type.startsWith("image/")) {
    showAlert("Please select an image file", "error");
    return;
  }

  selectedFile = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    const previewImage = document.getElementById("previewImage");
    const imagePreview = document.getElementById("imagePreview");
    if (previewImage) previewImage.src = e.target.result;
    if (imagePreview) imagePreview.classList.add("active");
  };
  reader.readAsDataURL(file);
}

// Setup Patient Form
function setupPatientForm() {
  const form = document.getElementById("patientForm");
  if (form) {
    form.addEventListener("submit", handleAnalyze);
  }
}

// Handle Analysis
async function handleAnalyze(e) {
  e.preventDefault();

  if (!selectedFile) {
    showAlert("Please upload an X-ray image first", "error");
    return;
  }

  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const btnText = submitBtn.querySelector(".btn-text");
  const btnLoader = submitBtn.querySelector(".btn-loader");

  // Show loading
  submitBtn.disabled = true;
  btnText.style.display = "none";
  btnLoader.style.display = "inline-flex";

  // Prepare form data
  const formData = new FormData();
  formData.append("image", selectedFile);
  formData.append("patient_name", form.patient_name.value);
  formData.append("patient_age", form.patient_age.value);
  formData.append("patient_gender", form.patient_gender.value);

  // Symptoms (checkboxes)
  const symptoms = [];
  form.querySelectorAll('input[name="symptoms"]:checked').forEach((cb) => {
    symptoms.push(cb.value);
  });
  formData.append("symptoms", symptoms.join(", ") || "None reported");

  formData.append("medical_history", form.medical_history.value || "");

  // Vital signs
  if (form.temperature.value) {
    formData.append("temperature", form.temperature.value);
  }
  if (form.oxygen_saturation.value) {
    formData.append("oxygen_saturation", form.oxygen_saturation.value);
  }
  if (form.heart_rate.value) {
    formData.append("heart_rate", form.heart_rate.value);
  }
  if (form.respiratory_rate.value) {
    formData.append("respiratory_rate", form.respiratory_rate.value);
  }

  try {
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      displayResults(data);
      showAlert("Analysis completed successfully!", "success");
    } else {
      showAlert(data.detail || "Analysis failed. Please try again.", "error");
    }
  } catch (error) {
    console.error("Analysis error:", error);
    showAlert("Network error. Please check your connection.", "error");
  } finally {
    submitBtn.disabled = false;
    btnText.style.display = "inline";
    btnLoader.style.display = "none";
  }
}

// Display Results
function displayResults(data) {
  const resultsSection = document.getElementById("resultsSection");
  const resultsContainer = document.getElementById("resultsContainer");

  if (!resultsSection || !resultsContainer) return;

  const severityColor =
    data.severity === "Severe"
      ? "var(--danger)"
      : data.severity === "Moderate"
      ? "var(--warning)"
      : data.severity === "Mild"
      ? "var(--secondary)"
      : "var(--info)";

  resultsContainer.innerHTML = `
        <div class="results-container">
            <div class="result-card">
                <h3 class="card-title">Diagnosis</h3>
                <div style="margin-top: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 0.9rem; color: var(--text-secondary);">Detected Condition</span>
                        <span style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary);">${
                          data.disease
                        }</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 0.9rem; color: var(--text-secondary);">Severity</span>
                        <span style="font-size: 1.25rem; font-weight: 700; color: ${severityColor};">${
    data.severity
  }</span>
                    </div>
                    <div style="margin-top: 1.5rem;">
                        <span style="font-size: 0.9rem; color: var(--text-secondary);">Confidence Level</span>
                        <div class="confidence-meter">
                            <div class="confidence-fill" style="width: ${
                              data.confidence
                            }%;"></div>
                        </div>
                        <span style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">${data.confidence.toFixed(
                          1
                        )}%</span>
                    </div>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h4 style="margin-bottom: 0.75rem; color: var(--text-primary);">Affected Regions</h4>
                    <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.5rem;">
                        ${data.affected_regions
                          .map(
                            (region) => `
                            <li style="padding: 0.5rem; background: var(--bg-secondary); border-radius: var(--radius-sm); border-left: 3px solid var(--primary);">
                                ${region}
                            </li>
                        `
                          )
                          .join("")}
                    </ul>
                </div>
            </div>
            
            <div class="result-card">
                <h3 class="card-title">Clinical Recommendations</h3>
                <ul class="recommendations-list">
                    ${data.recommendations
                      .map(
                        (rec) => `
                        <li>${rec}</li>
                    `
                      )
                      .join("")}
                </ul>
                
                <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color);">
                    <button class="btn btn-primary btn-block" onclick="downloadReport(${
                      data.analysis_id
                    })">
                        📄 Download PDF Report
                    </button>
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 2rem;">
            <h3 class="card-title">Visual Analysis (Grad-CAM)</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                The heatmap below highlights the regions that influenced the AI's decision.
            </p>
            <div style="text-align: center;">
                <img src="${API_URL}/api/image/gradcam/${data.analysis_id}" 
                     alt="Grad-CAM visualization" 
                     style="width: 100%; max-width: 600px; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg);">
            </div>
        </div>
    `;

  resultsSection.classList.remove("hidden");
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Download Report (Global function)
window.downloadReport = async function (analysisId) {
  try {
    const response = await fetch(
      `${API_URL}/api/download/report/${analysisId}`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      }
    );

    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `medical_report_${analysisId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showAlert("Report downloaded successfully!", "success");
    } else {
      showAlert("Failed to download report", "error");
    }
  } catch (error) {
    console.error("Download error:", error);
    showAlert("Failed to download report", "error");
  }
};

// Logout Handler
function handleLogout() {
  localStorage.removeItem("token");
  localStorage.removeItem("doctorName");
  localStorage.removeItem("doctorId");
  window.location.href = "index.html";
}

// Show Alert
function showAlert(message, type = "info") {
  const alert = document.createElement("div");
  alert.className = `alert alert-${type}`;
  alert.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        z-index: 9999;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;
  alert.textContent = message;
  document.body.appendChild(alert);

  setTimeout(() => {
    alert.style.animation = "slideOut 0.3s ease-out";
    setTimeout(() => alert.remove(), 300);
  }, 5000);
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initAnalysisPage();

  // Logout button
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      handleLogout();
    });
  }
});
