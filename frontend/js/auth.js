const API_URL = "http://localhost:8000"; // Change this to your backend URL

// Theme Management
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

// Form Switching
function setupFormSwitching() {
  const showRegister = document.getElementById("showRegister");
  const showLogin = document.getElementById("showLogin");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  if (showRegister) {
    showRegister.addEventListener("click", (e) => {
      e.preventDefault();
      loginForm.style.display = "none";
      registerForm.style.display = "block";
      hideAlert();
    });
  }

  if (showLogin) {
    showLogin.addEventListener("click", (e) => {
      e.preventDefault();
      registerForm.style.display = "none";
      loginForm.style.display = "block";
      hideAlert();
    });
  }
}

// Alert Functions
function showAlert(message, type = "info") {
  const alertBox = document.getElementById("alertBox");
  if (!alertBox) {
    // Create floating alert if no alert box exists
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
    return;
  }

  alertBox.textContent = message;
  alertBox.className = `alert alert-${type}`;
  alertBox.style.display = "flex";

  setTimeout(() => {
    hideAlert();
  }, 5000);
}

function hideAlert() {
  const alertBox = document.getElementById("alertBox");
  if (alertBox) {
    alertBox.style.display = "none";
  }
}

// Login Handler
async function handleLogin(e) {
  e.preventDefault();

  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const btnText = submitBtn.querySelector(".btn-text");
  const btnLoader = submitBtn.querySelector(".btn-loader");

  // Show loading state
  submitBtn.disabled = true;
  btnText.style.display = "none";
  btnLoader.style.display = "inline-flex";

  const formData = {
    email: form.email.value,
    password: form.password.value,
  };

  try {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (response.ok) {
      // Store token and user info
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("doctorName", data.doctor_name);
      localStorage.setItem("doctorId", data.doctor_id);

      showAlert("Login successful! Redirecting...", "success");

      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 1000);
    } else {
      showAlert(
        data.detail || "Login failed. Please check your credentials.",
        "error"
      );
    }
  } catch (error) {
    console.error("Login error:", error);
    showAlert("Network error. Please check your connection.", "error");
  } finally {
    submitBtn.disabled = false;
    btnText.style.display = "inline";
    btnLoader.style.display = "none";
  }
}

// Register Handler
async function handleRegister(e) {
  e.preventDefault();

  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const btnText = submitBtn.querySelector(".btn-text");
  const btnLoader = submitBtn.querySelector(".btn-loader");

  // Show loading state
  submitBtn.disabled = true;
  btnText.style.display = "none";
  btnLoader.style.display = "inline-flex";

  const formData = {
    name: form.name.value,
    email: form.email.value,
    password: form.password.value,
    specialty: form.specialty.value,
    license_number: form.license_number.value,
  };

  // Basic validation
  if (formData.password.length < 8) {
    showAlert("Password must be at least 8 characters long", "error");
    submitBtn.disabled = false;
    btnText.style.display = "inline";
    btnLoader.style.display = "none";
    return;
  }

  try {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (response.ok) {
      // Store token and user info
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("doctorName", data.doctor_name);
      localStorage.setItem("doctorId", data.doctor_id);

      showAlert("Registration successful! Redirecting...", "success");

      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 1000);
    } else {
      showAlert(
        data.detail || "Registration failed. Please try again.",
        "error"
      );
    }
  } catch (error) {
    console.error("Registration error:", error);
    showAlert("Network error. Please check your connection.", "error");
  } finally {
    submitBtn.disabled = false;
    btnText.style.display = "inline";
    btnLoader.style.display = "none";
  }
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupFormSwitching();

  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
  }

  if (registerForm) {
    registerForm.addEventListener("submit", handleRegister);
  }

  // Check if already logged in
  if (localStorage.getItem("token")) {
    window.location.href = "dashboard.html";
  }
});
