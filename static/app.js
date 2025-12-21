/**
 * Main application script for Velgo Agri Solution (MongoDB version)
 * Replaces Firebase with JWT authentication
 */

// Import auth module functions
// Note: This script expects auth.js to be loaded first

// --- Global App State ---
let currentLang = 'en'; // Default is English
let myBookingsInterval = null; // Polling interval for My Bookings

// --- Modal Element Refs ---
let consultationModal, bookingModal, loginModal, myBookingsModal, bookingServiceNameInput;

// --- Language Toggle ---
window.toggleLanguage = function () {
    currentLang = currentLang === 'en' ? 'ta' : 'en';
    const elements = document.querySelectorAll('[data-en][data-ta]');
    elements.forEach(el => {
        const textEl = el.querySelector('.btn-text') || el;
        const text = el.getAttribute('data-' + currentLang);
        if (text) {
            textEl.textContent = text;
        }
    });

    const langBtn = document.getElementById('langBtn');
    if (langBtn) {
        langBtn.textContent = currentLang === 'en' ? 'தமிழ்' : 'English';
    }
};

// --- Scroll Header Effect ---
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// --- Falling Leaves Animation ---
function createFallingLeaves() {
    const leavesContainer = document.querySelector('.falling-leaves');
    if (!leavesContainer) return;

    const leafChars = ['🍂', '🌿', '🍃'];
    const animations = ['fall', 'fall-windy', 'fall-reverse'];

    for (let i = 0; i < 15; i++) {
        const leaf = document.createElement('div');
        leaf.className = 'leaf';
        leaf.textContent = leafChars[Math.floor(Math.random() * leafChars.length)];
        leaf.style.left = `${Math.random() * 100}%`;
        leaf.style.animationName = animations[Math.floor(Math.random() * animations.length)];
        leaf.style.animationDuration = `${10 + Math.random() * 15}s`;
        leaf.style.animationDelay = `${Math.random() * 10}s`;
        leaf.style.fontSize = `${1 + Math.random()}rem`;
        leavesContainer.appendChild(leaf);
    }
}

// --- Button Loading State Helpers ---
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}

// --- Login/Signup Form Handlers ---
window.handleLogin = async function (event) {
    event.preventDefault();
    clearAuthErrors();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const email = form.querySelector('[name="email"]').value.trim();
    const password = form.querySelector('[name="password"]').value.trim();

    setButtonLoading(submitBtn, true);

    const result = await loginUser(email, password);

    setButtonLoading(submitBtn, false);

    if (result.success) {
        closeLoginModal();
        form.reset();
        alert('Login successful!');
    } else {
        showAuthError('login-error', result.message);
    }
};

window.handleSignup = async function (event) {
    event.preventDefault();
    clearAuthErrors();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const email = form.querySelector('[name="email"]').value.trim();
    const password = form.querySelector('[name="password"]').value.trim();

    if (password.length < 6) {
        showAuthError('signup-error', 'Password must be at least 6 characters long.');
        return;
    }

    setButtonLoading(submitBtn, true);

    const result = await registerUser(email, password);

    setButtonLoading(submitBtn, false);

    if (result.success) {
        closeLoginModal();
        form.reset();
        alert('Registration successful! You are now logged in.');
    } else {
        showAuthError('signup-error', result.message);
    }
};

function showAuthError(formId, message) {
    const errorEl = document.getElementById(formId);
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

function clearAuthErrors() {
    document.querySelectorAll('.auth-error').forEach(el => {
        el.textContent = '';
        el.style.display = 'none';
    });
}

// --- Modal Functions ---
window.openLoginModal = function () {
    loginModal.style.display = 'block';
    showTab('login-tab', document.querySelector('.tab-btn'));
};

window.closeLoginModal = function () {
    loginModal.style.display = 'none';
    clearAuthErrors();
};

window.showTab = function (tabId, button) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    button.classList.add('active');
};

window.openConsultationModal = function () {
    if (!isLoggedIn()) {
        openLoginModal();
        return;
    }
    consultationModal.style.display = 'block';
    document.getElementById('consultationOptions').style.display = 'flex';
    document.getElementById('consultationForm').style.display = 'none';
};

window.closeConsultationModal = function () {
    consultationModal.style.display = 'none';
};

window.selectConsultationType = function (type) {
    document.getElementById('consultationType').value = type;
    document.getElementById('consultationOptions').style.display = 'none';
    document.getElementById('consultationForm').style.display = 'block';
};

window.openBookingModal = function (serviceNameEn, serviceNameTa) {
    if (!isLoggedIn()) {
        openLoginModal();
        return;
    }
    const serviceName = (currentLang === 'en') ? serviceNameEn : serviceNameTa;
    bookingServiceNameInput.value = serviceName;
    bookingModal.style.display = 'block';
};

window.closeBookingModal = function () {
    bookingModal.style.display = 'none';
};

window.openMyBookingsModal = function () {
    if (!isLoggedIn()) {
        openLoginModal();
        return;
    }
    myBookingsModal.style.display = 'block';
    loadMyBookings(); // Load immediately
    startBookingsPolling(); // Start polling
};

window.closeMyBookingsModal = function () {
    myBookingsModal.style.display = 'none';
    stopBookingsPolling(); // Stop polling when modal closes
};

window.showBookingTab = function (tabId, button) {
    window.showTab(tabId, button);
};

// Close modals when clicking outside
window.onclick = function (event) {
    if (event.target == consultationModal) { closeConsultationModal(); }
    if (event.target == bookingModal) { closeBookingModal(); }
    if (event.target == loginModal) { closeLoginModal(); }
    if (event.target == myBookingsModal) { closeMyBookingsModal(); }
};

// --- Form Submission Handlers ---
window.handleConsultationSubmit = async function (event) {
    event.preventDefault();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const data = {
        type: document.getElementById('consultationType').value,
        name: document.getElementById('name').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        landSize: document.getElementById('landSize').value || '',
        message: document.getElementById('message').value || ''
    };

    setButtonLoading(submitBtn, true);

    try {
        const response = await fetch('/api/consult', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeader()
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        setButtonLoading(submitBtn, false);

        if (response.ok && result.status === 'success') {
            alert('Consultation request submitted successfully!');
            form.reset();
            closeConsultationModal();
        } else {
            alert('Error: ' + (result.message || 'Failed to submit consultation request.'));
        }
    } catch (error) {
        setButtonLoading(submitBtn, false);
        console.error('Error submitting consultation:', error);
        alert('Network error. Please try again.');
    }
};

window.handleBookingSubmit = async function (event) {
    event.preventDefault();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const data = {
        service: document.getElementById('bookingService').value,
        name: document.getElementById('bookingName').value,
        phone: document.getElementById('bookingPhone').value,
        location: document.getElementById('bookingLocation').value,
        email: document.getElementById('bookingEmail').value || '',
        message: document.getElementById('bookingMessage').value || ''
    };

    setButtonLoading(submitBtn, true);

    try {
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeader()
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        setButtonLoading(submitBtn, false);

        if (response.ok && result.status === 'success') {
            alert('Service booking submitted successfully!');
            form.reset();
            closeBookingModal();
        } else {
            alert('Error: ' + (result.message || 'Failed to submit booking.'));
        }
    } catch (error) {
        setButtonLoading(submitBtn, false);
        console.error('Error submitting booking:', error);
        alert('Network error. Please try again.');
    }
};

// --- My Bookings Functionality ---
async function loadMyBookings() {
    try {
        // Fetch consultations
        const consultResponse = await fetch('/api/my-consultations', {
            headers: getAuthHeader()
        });

        if (consultResponse.ok) {
            const consultData = await consultResponse.json();
            if (consultData.status === 'success') {
                renderBookings(consultData.consultations, 'consultations');
            }
        }

        // Fetch bookings
        const bookingsResponse = await fetch('/api/my-bookings', {
            headers: getAuthHeader()
        });

        if (bookingsResponse.ok) {
            const bookingsData = await bookingsResponse.json();
            if (bookingsData.status === 'success') {
                renderBookings(bookingsData.bookings, 'bookings');
            }
        }
    } catch (error) {
        console.error('Error loading my bookings:', error);
    }
}

function startBookingsPolling() {
    // Poll every 5 seconds
    myBookingsInterval = setInterval(loadMyBookings, 5000);
}

function stopBookingsPolling() {
    if (myBookingsInterval) {
        clearInterval(myBookingsInterval);
        myBookingsInterval = null;
    }
}

function renderBookings(bookings, type) {
    // Get containers
    const activeContainer = document.getElementById(`my-${type}-list-active`);
    const historyContainer = document.getElementById(`my-${type}-list-history`);
    if (!activeContainer || !historyContainer) return;

    // Filter lists
    const activeList = bookings.filter(b => b.status === 'pending' || b.status === 'accepted');
    const historyList = bookings.filter(b => b.status === 'completed' || b.status === 'rejected');

    // Render Active List
    buildBookingCards(activeContainer, activeList, type, 'active');

    // Render History List
    buildBookingCards(historyContainer, historyList, type, 'history');

    // Re-apply language
    if (currentLang === 'ta') {
        currentLang = 'en';
        toggleLanguage();
    }
}

function buildBookingCards(container, list, type, listCategory) {
    container.innerHTML = '';

    if (list.length === 0) {
        let noDataEn, noDataTa;
        if (type === 'consultations') {
            noDataEn = (listCategory === 'active') ? "You have no active consultation requests." : "You have no past consultations.";
            noDataTa = (listCategory === 'active') ? "உங்களிடம் செயலில் உள்ள ஆலோசனை கோரிக்கைகள் எதுவும் இல்லை." : "உங்களிடம் கடந்தகால ஆலோசனைகள் எதுவும் இல்லை.";
        } else {
            noDataEn = (listCategory === 'active') ? "You have no active service bookings." : "You have no past service bookings.";
            noDataTa = (listCategory === 'active') ? "உங்களிடம் செயலில் உள்ள சேவை பதிவுகள் எதுவும் இல்லை." : "உங்களிடம் கடந்தகால சேவை பதிவுகள் எதுவும் இல்லை.";
        }
        container.innerHTML = `<p class="no-bookings" data-en="${noDataEn}" data-ta="${noDataTa}">${currentLang === 'en' ? noDataEn : noDataTa}</p>`;
        return;
    }

    list.forEach(booking => {
        const card = document.createElement('div');
        card.className = 'booking-card';

        const title = type === 'consultations' ? (booking.type || 'Consultation') : (booking.service || 'Service Booking');
        const timestamp = booking.timestamp ? new Date(booking.timestamp).toLocaleString() : 'No date';

        const status = booking.status || 'pending';
        const statusText = status.charAt(0).toUpperCase() + status.slice(1);

        let statusMessageHTML = '';
        if (status === 'accepted') {
            statusMessageHTML = `<div class="booking-status-message status-msg-accepted">
                <i class="fas fa-check-circle"></i> Your request has been accepted! We will contact you soon.
            </div>`;
        } else if (status === 'completed') {
            statusMessageHTML = `<div class="booking-status-message status-msg-completed">
                <i class="fas fa-check-double"></i> This request has been completed. Thank you!
            </div>`;
        } else if (status === 'rejected') {
            const reason = booking.rejection_reason || 'No reason provided.';
            statusMessageHTML = `<div class="booking-status-message status-msg-rejected">
                <strong>Rejection Reason:</strong> ${reason}
            </div>`;
        }

        card.innerHTML = `
            <div class="booking-card-header">
                <h4>${title}</h4>
                <span class="status status-${status}">${statusText}</span>
            </div>
            <div class="booking-card-body">
                <p><strong>Name:</strong> ${booking.name || 'N/A'}</p>
                <p><strong>Phone:</strong> ${booking.phone || 'N/A'}</p>
                <p><strong>Submitted:</strong> ${timestamp}</p>
            </div>
            ${statusMessageHTML}
        `;

        container.appendChild(card);
    });
}

// --- Footer Credits Loading ---
async function loadFooterData() {
    try {
        const response = await fetch('/api/config/footer');
        if (response.ok) {
            const data = await response.json();
            if (data.status === 'success') {
                const copyrightP = document.getElementById('copyright-text');
                const currentYear = new Date().getFullYear();
                const companyName = 'Velgo Agrisolutions Pvt. Ltd.';

                copyrightP.innerHTML = `&copy; ${currentYear} ${companyName} 
                    <span data-en="All rights reserved." data-ta="அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.">All rights reserved.</span>
                    <a href="team.html" target="_blank" class="footer-credits-link">
                        <span class="footer-credits"> | ${data.credits}</span>
                    </a>`;

                // Re-apply language if needed
                if (currentLang === 'ta') {
                    currentLang = 'en';
                    toggleLanguage();
                }
            }
        }
    } catch (error) {
        console.error('Error loading footer credits:', error);
    }
}

// --- DOMContentLoaded - Initialize Everything ---
document.addEventListener('DOMContentLoaded', () => {
    // Initialize auth system
    initAuth();

    // Initialize AOS
    AOS.init({ once: true, offset: 20 });

    // Create falling leaves
    createFallingLeaves();

    // Get modal references
    consultationModal = document.getElementById('consultationModal');
    bookingModal = document.getElementById('bookingModal');
    loginModal = document.getElementById('loginModal');
    myBookingsModal = document.getElementById('myBookingsModal');
    bookingServiceNameInput = document.getElementById('bookingService');

    // Attach form listeners
    document.getElementById('consultationForm').addEventListener('submit', handleConsultationSubmit);
    document.getElementById('bookingForm').addEventListener('submit', handleBookingSubmit);
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('signup-form').addEventListener('submit', handleSignup);

    // Load footer data
    loadFooterData();
});

// Right-click protection
document.addEventListener('contextmenu', function (e) {
    e.preventDefault();
});

// Keyboard shortcuts protection
document.addEventListener('keydown', function (e) {
    if (e.key === 'F12') e.preventDefault();
    if (e.ctrlKey && e.shiftKey && ['I', 'J', 'C'].includes(e.key.toUpperCase())) e.preventDefault();
    if (e.ctrlKey && e.key.toUpperCase() === 'U') e.preventDefault();
});
