/**
 * Authentication Module for Velgo Agri Solution
 * JWT-based authentication replacing Firebase
 */

// Storage keys
const TOKEN_KEY = 'velgo_auth_token';
const USER_KEY = 'velgo_user_data';

// Current user state
let currentUser = null;
let currentToken = null;

// Initialize auth on page load
function initAuth() {
    // Check if user is already logged in
    const token = localStorage.getItem(TOKEN_KEY);
    const userData = localStorage.getItem(USER_KEY);
    
    if (token && userData) {
        try {
            currentToken = token;
            currentUser = JSON.parse(userData);
            updateUIForLoggedInUser();
            
            // If admin, may need to redirect
            if (currentUser.role === 'admin' && window.location.pathname === '/') {
                // Optional: auto-redirect admin to /admin panel
                // Commenting this out to allow admins to view homepage too
                // setTimeout(() => window.location.href = '/admin', 1000);
            }
        } catch (e) {
            console.error('Error parsing stored user data:', e);
            clearAuth();
        }
    } else {
        updateUIForLoggedOutUser();
    }
}

// User Registration
async function registerUser(email, password) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            // Save token and user data
            localStorage.setItem(TOKEN_KEY, data.token);
            localStorage.setItem(USER_KEY, JSON.stringify(data.user));
            currentToken = data.token;
            currentUser = data.user;
            
            updateUIForLoggedInUser();
            return { success: true, user: data.user };
        } else {
            return { success: false, message: data.message || 'Registration failed' };
        }
    } catch (error) {
        console.error('Registration error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

// User Login
async function loginUser(email, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            // Save token and user data
            localStorage.setItem(TOKEN_KEY, data.token);
            localStorage.setItem(USER_KEY, JSON.stringify(data.user));
            currentToken = data.token;
            currentUser = data.user;
            
            updateUIForLoggedInUser();
            
            // If admin, redirect to admin panel
            if (data.user.role === 'admin') {
                setTimeout(() => {
                    window.location.href = '/admin';
                }, 500);
            }
            
            return { success: true, user: data.user };
        } else {
            return { success: false, message: data.message || 'Login failed' };
        }
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

// User Logout
function logoutUser() {
    clearAuth();
    updateUIForLoggedOutUser();
    
    // Redirect to homepage if on admin panel
    if (window.location.pathname.includes('/admin')) {
        window.location.href = '/';
    }
}

// Clear auth data
function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    currentToken = null;
    currentUser = null;
}

// Update UI for logged-in user
function updateUIForLoggedInUser() {
    const userStatus = document.getElementById('user-status');
    if (!userStatus) return;
    
    const userEmail = currentUser ? currentUser.email.split('@')[0] : 'User';
    const isAdmin = currentUser && currentUser.role === 'admin';
    
    let html = `<span>Welcome, <strong>${userEmail}</strong></span>`;
    
    // Add "My Bookings" button for regular users
    if (!isAdmin) {
        html += `<button class="login-btn" onclick="openMyBookingsModal()">My Bookings</button>`;
    }
    
    // Add "Admin Panel" button for admins
    if (isAdmin) {
        html += `<a href="/admin" class="login-btn admin-btn">Admin Panel</a>`;
    }
    
    html += `<button class="logout-btn" onclick="logoutUser()">Logout</button>`;
    
    userStatus.innerHTML = html;
}

// Update UI for logged-out user
function updateUIForLoggedOutUser() {
    const userStatus = document.getElementById('user-status');
    if (!userStatus) return;
    
    userStatus.innerHTML = `<button class="login-btn" onclick="openLoginModal()">Login</button>`;
}

// Get authorization header for API calls
function getAuthHeader() {
    if (!currentToken) {
        return {};
    }
    return {
        'Authorization': `Bearer ${currentToken}`
    };
}

// Check if user is logged in
function isLoggedIn() {
    return currentToken !== null && currentUser !== null;
}

// Check if user is admin
function isAdmin() {
    return isLoggedIn() && currentUser.role === 'admin';
}

// Export functions for global use
window.initAuth = initAuth;
window.registerUser = registerUser;
window.loginUser = loginUser;
window.logoutUser = logoutUser;
window.getAuthHeader = getAuthHeader;
window.isLoggedIn = isLoggedIn;
window.isAdmin = isAdmin;
window.currentUser = () => currentUser;
