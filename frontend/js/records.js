const API_URL = "http://localhost:8000";

// Check Authentication
function checkAuth() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "index.html";
    return false;
  }
  return token;
}

// Get Auth Headers
function getAuthHeaders() {
  return {
    Authorization: `Bearer ${localStorage.getItem("token")}`,
    "Content-Type": "application/json",
  };
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

// Initialize Records Page
async function initRecordsPage() {
  checkAuth();
  updateUserInfo();
  await loadAllRecords();
  setupSearch();
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

// Load All Records
async function loadAllRecords() {
  try {
    const response = await fetch(`${API_URL}/api/records`, {
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const data = await response.json();
      displayRecords(data.records);
    }
  } catch (error) {
    console.error("Error loading records:", error);
    showAlert("Failed to load records", "error");
  }
}

// Display Records in Table
function displayRecords(records) {
  const tbody = document.getElementById("recordsTable");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (records.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">No records found</p>
                    <p style="font-size: 0.9rem;">Start analyzing X-rays to see records here</p>
                </td>
            </tr>
        `;
    return;
  }

  records.forEach((record) => {
    const row = document.createElement("tr");

    const severityClass =
      record.severity === "Severe"
        ? "danger"
        : record.severity === "Moderate"
        ? "warning"
        : record.severity === "Mild"
        ? "success"
        : "info";

    const date = new Date(record.timestamp).toLocaleString();

    row.innerHTML = `
            <td><strong>${record.patient_name}</strong></td>
            <td>${record.patient_age} years, ${record.patient_gender}</td>
            <td>${record.disease}</td>
            <td><span class="badge badge-${severityClass}">${
      record.severity
    }</span></td>
            <td>${record.confidence.toFixed(1)}%</td>
            <td>${date}</td>
        `;

    row.style.cursor = "pointer";
    row.addEventListener("click", () => {
      viewRecordDetail(record.id);
    });

    tbody.appendChild(row);
  });
}

// View Record Detail
async function viewRecordDetail(analysisId) {
  try {
    const response = await fetch(`${API_URL}/api/records/${analysisId}`, {
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const data = await response.json();
      showRecordModal(data, analysisId);
    }
  } catch (error) {
    console.error("Error loading record detail:", error);
    showAlert("Failed to load record details", "error");
  }
}

// Show Record Detail Modal
function showRecordModal(data, analysisId) {
  const modal = document.createElement("div");
  modal.className = "modal-overlay";
  modal.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        padding: 1rem;
        overflow-y: auto;
    `;

  const vitalSigns = data.analysis.vital_signs;
  const hasVitals =
    vitalSigns.temperature ||
    vitalSigns.oxygen_saturation ||
    vitalSigns.heart_rate ||
    vitalSigns.respiratory_rate;

  const severityClass =
    data.analysis.severity === "Severe"
      ? "danger"
      : data.analysis.severity === "Moderate"
      ? "warning"
      : data.analysis.severity === "Mild"
      ? "success"
      : "info";

  modal.innerHTML = `
        <div class="card" style="max-width: 800px; width: 100%; max-height: 90vh; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="color: var(--text-primary);">Patient Record Details</h2>
                <button onclick="this.closest('.modal-overlay').remove()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-secondary);">
                    ✕
                </button>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                <div>
                    <h3 style="color: var(--text-primary); margin-bottom: 1rem;">Patient Information</h3>
                    <p><strong>Name:</strong> ${data.patient.name}</p>
                    <p><strong>Age:</strong> ${data.patient.age} years</p>
                    <p><strong>Gender:</strong> ${data.patient.gender}</p>
                    ${
                      data.patient.medical_history
                        ? `<p><strong>Medical History:</strong> ${data.patient.medical_history}</p>`
                        : ""
                    }
                </div>
                
                <div>
                    <h3 style="color: var(--text-primary); margin-bottom: 1rem;">Analysis Results</h3>
                    <p><strong>Disease:</strong> ${data.analysis.disease}</p>
                    <p><strong>Severity:</strong> <span class="badge badge-${severityClass}">${
    data.analysis.severity
  }</span></p>
                    <p><strong>Confidence:</strong> ${data.analysis.confidence.toFixed(
                      1
                    )}%</p>
                    <p><strong>Date:</strong> ${new Date(
                      data.analysis.timestamp
                    ).toLocaleString()}</p>
                </div>
            </div>
            
            ${
              hasVitals
                ? `
            <div style="margin-bottom: 2rem;">
                <h3 style="color: var(--text-primary); margin-bottom: 1rem;">Vital Signs</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    ${
                      vitalSigns.temperature
                        ? `<div><strong>Temperature:</strong> ${vitalSigns.temperature}°C</div>`
                        : ""
                    }
                    ${
                      vitalSigns.oxygen_saturation
                        ? `<div><strong>O₂ Saturation:</strong> ${vitalSigns.oxygen_saturation}%</div>`
                        : ""
                    }
                    ${
                      vitalSigns.heart_rate
                        ? `<div><strong>Heart Rate:</strong> ${vitalSigns.heart_rate} bpm</div>`
                        : ""
                    }
                    ${
                      vitalSigns.respiratory_rate
                        ? `<div><strong>Resp. Rate:</strong> ${vitalSigns.respiratory_rate} breaths/min</div>`
                        : ""
                    }
                </div>
            </div>
            `
                : ""
            }
            
            <div style="margin-bottom: 2rem;">
                <h3 style="color: var(--text-primary); margin-bottom: 1rem;">Symptoms</h3>
                <p>${data.analysis.symptoms}</p>
            </div>
            
            <div style="margin-bottom: 2rem;">
                <h3 style="color: var(--text-primary); margin-bottom: 1rem;">Recommendations</h3>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.5rem;">
                    ${data.analysis.recommendations
                      .split(", ")
                      .map(
                        (rec) => `
                        <li style="padding: 0.75rem; background: var(--bg-secondary); border-radius: var(--radius-md); border-left: 3px solid var(--primary);">
                            ${rec}
                        </li>
                    `
                      )
                      .join("")}
                </ul>
            </div>
            
            <div style="display: flex; gap: 1rem;">
                <button class="btn btn-primary" onclick="downloadReport(${analysisId})">
                    📄 Download Report
                </button>
                <button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">
                    Close
                </button>
            </div>
        </div>
    `;

  document.body.appendChild(modal);

  // Close on outside click
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
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

// Setup Search
function setupSearch() {
  const searchInput = document.getElementById("searchRecords");
  if (!searchInput) return;

  searchInput.addEventListener("input", (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const rows = document.querySelectorAll("#recordsTable tr");

    rows.forEach((row) => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(searchTerm) ? "" : "none";
    });
  });
}

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
  initRecordsPage();

  // Logout button
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      handleLogout();
    });
  }
});
