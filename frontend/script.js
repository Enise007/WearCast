// API Configuration 
// Change this url to your own backend url
const API_BASE_URL ='http://127.0.0.1:5000';

// State Management
let currentUser = null;
let currentConversationId = null;
let conversations = [];
let messages = [];

let isSending = false;


// DOM Elements
const elements = {
    // Auth elements
    authButtons: document.getElementById('authButtons'),
    userProfile: document.getElementById('userProfile'),
    userName: document.getElementById('userName'),
    loginBtn: document.getElementById('loginBtn'),
    registerBtn: document.getElementById('registerBtn'),
    logoutBtn: document.getElementById('logoutBtn'),

    // Modal elements
    loginModal: document.getElementById('loginModal'),
    registerModal: document.getElementById('registerModal'),
    closeLoginModal: document.getElementById('closeLoginModal'),
    closeRegisterModal: document.getElementById('closeRegisterModal'),
    profileModal: document.getElementById('profileModal'),
    closeProfileModal: document.getElementById('closeProfileModal'),

    // Form elements
    loginForm: document.getElementById('loginForm'),
    registerForm: document.getElementById('registerForm'),

    // Chat elements
    sidebar: document.getElementById('sidebar'),
    conversationsList: document.getElementById('conversationsList'),
    newChatBtn: document.getElementById('newChatBtn'),
    chatContainer: document.getElementById('chatContainer'),
    welcomeMessage: document.getElementById('welcomeMessage'),
    messagesContainer: document.getElementById('messagesContainer'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    themeToggleBtn: document.getElementById('themeToggleBtn'),

    // Loading
    loadingOverlay: document.getElementById('loadingOverlay'),
    // Toasts
    toastContainer: document.getElementById('toastContainer'),
    // Confirm modal
    confirmModal: document.getElementById('confirmModal'),
    confirmCancelBtn: document.getElementById('confirmCancelBtn'),
    confirmDeleteBtn: document.getElementById('confirmDeleteBtn'),
    confirmTitle: document.getElementById('confirmTitle'),
    confirmText: document.getElementById('confirmText'),
    // Input modal
    inputModal: document.getElementById('inputModal'),
    inputTitle: document.getElementById('inputTitle'),
    inputLabel: document.getElementById('inputLabel'),
    inputField: document.getElementById('inputField'),
    inputCancelBtn: document.getElementById('inputCancelBtn'),
    inputOkBtn: document.getElementById('inputOkBtn'),

    // Profile form controls
    pfFirstName: document.getElementById('pfFirstName'),
    pfLastName: document.getElementById('pfLastName'),
    pfEmail: document.getElementById('pfEmail'),
    pfBirthdate: document.getElementById('pfBirthdate'),
    pfAgeDisplay: document.getElementById('pfAgeDisplay'),
    pfGender: document.getElementById('pfGender'),
    pfCity: document.getElementById('pfCity'), // backend destekliyorsa
    profileForm: document.getElementById('profileForm'),
    profileSaveBtn: document.getElementById('profileSaveBtn'),
    profileDeleteBtn: document.getElementById('profileDeleteBtn'),
    profileCancelBtn: document.getElementById('profileCancelBtn'),
    // Account modal
    accountModal: document.getElementById('accountModal'),
    closeAccountModal: document.getElementById('closeAccountModal'),
    openAccountBtn: document.getElementById('openAccountBtn'),
    emailForm: document.getElementById('emailForm'),
    passwordForm: document.getElementById('passwordForm'),
    newEmail: document.getElementById('newEmail'),
    emailPassword: document.getElementById('emailPassword'),
    currentPassword: document.getElementById('currentPassword'),
    newPassword: document.getElementById('newPassword'),

};

// Utility Functions
function showLoading() {
    if (elements.loadingOverlay) elements.loadingOverlay.style.display = 'flex';
}
function hideLoading() {
    if (elements.loadingOverlay) elements.loadingOverlay.style.display = 'none';
}

// >>> ADD: Gönderim sırasında input/btn kilidi
function setInputDisabled(disabled) {
    if (elements.messageInput) elements.messageInput.disabled = disabled;
    if (elements.sendBtn) {
        elements.sendBtn.disabled = disabled;
        elements.sendBtn.classList.toggle('disabled', disabled); // CSS'in varsa
    }
}
// Toast helpers
function showToast(message, type = 'info', options = {}) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const msg = document.createElement('div');
    msg.className = 'toast-message';
    msg.textContent = message;
    toast.appendChild(msg);

    if (options.actions && options.actions.length) {
        const actions = document.createElement('div');
        actions.className = 'toast-actions';
        options.actions.forEach(({ label, onClick, variant }) => {
            const btn = document.createElement('button');
            btn.className = `toast-btn ${variant || ''}`.trim();
            btn.textContent = label;
            btn.addEventListener('click', () => {
                onClick?.();
                toast.remove();
            });
            actions.appendChild(btn);
        });
        toast.appendChild(actions);
    }

    elements.toastContainer.appendChild(toast);

    const duration = options.duration ?? 3000;
    if (duration > 0) {
        setTimeout(() => toast.remove(), duration);
    }
    return toast;
}
function showError(message) { showToast(message, 'error', { duration: 4000 }); }
function showSuccess(message) { showToast(message, 'success', { duration: 2500 }); }

// Confirm modal helpers
let pendingConfirm = null; // { onConfirm: fn }
function openConfirm({ title, text, onConfirm }) {
    elements.confirmTitle.textContent = title || 'Onayla';
    elements.confirmText.textContent = text || '';
    pendingConfirm = { onConfirm };
    elements.confirmModal.classList.add('show');
}
function closeConfirm() {
    elements.confirmModal.classList.remove('show');
    pendingConfirm = null;
}

// Centered input modal for rename
let pendingInput = null; // { onSubmit: fn }
function openInput({ title, label, placeholder, value, onSubmit }) {
    elements.inputTitle.textContent = title || 'Girdi gerekli';
    elements.inputLabel.textContent = label || '';
    elements.inputField.placeholder = placeholder || '';
    elements.inputField.value = value || '';
    pendingInput = { onSubmit };
    elements.inputModal.classList.add('show');
    setTimeout(() => elements.inputField.focus(), 0);
}
function closeInput() {
    elements.inputModal.classList.remove('show');
    pendingInput = null;
}

// Theme utilities
function applySavedThemePreference() {
    let savedTheme = localStorage.getItem('theme');
    if (!savedTheme) {
        savedTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
    }
    if (savedTheme === 'dark') {
        document.body.classList.add('dark');
        updateThemeToggleIcon('dark');
    } else {
        document.body.classList.remove('dark');
        updateThemeToggleIcon('light');
    }
}
function toggleTheme() {
    const willEnableDark = !document.body.classList.contains('dark');
    document.body.classList.toggle('dark');
    localStorage.setItem('theme', willEnableDark ? 'dark' : 'light');
    updateThemeToggleIcon(willEnableDark ? 'dark' : 'light');
}
function updateThemeToggleIcon(mode) {
    if (!elements.themeToggleBtn) return;
    const icon = elements.themeToggleBtn.querySelector('i');
    if (!icon) return;
    if (mode === 'dark') {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Calculate age from birthdate
function calculateAge(birthdate) {
    if (!birthdate) return null;
    const today = new Date();
    const birthDate = new Date(birthdate);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    return age;
}

// Validate birthdate
function validateBirthdate(birthdate) {
    if (!birthdate) return { valid: false, message: 'Birth date is required' };
    
    const today = new Date();
    const birthDate = new Date(birthdate);
    const age = calculateAge(birthdate);
    
    if (birthDate > today) {
        return { valid: false, message: 'Birth date cannot be in the future' };
    }
    
    if (age < 1 || age > 120) {
        return { valid: false, message: 'Age must be between 1 and 120 years' };
    }
    
    return { valid: true, age: age };
}

// Validate password
function validatePassword(password) {
    if (!password) return { valid: false, message: 'Password is required' };
    
    if (password.length < 6) {
        return { valid: false, message: 'Password must be at least 6 characters long' };
    }
    
    const hasLowercase = /[a-z]/.test(password);
    const hasUppercase = /[A-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    
    if (!hasLowercase || !hasUppercase || !hasNumber) {
        return { 
            valid: false, 
            message: 'Password must contain at least 1 lowercase letter, 1 uppercase letter, and 1 number' 
        };
    }
    
    return { valid: true };
}

// Format birthdate for display (YYYY-MM-DD)
function formatBirthdateForInput(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
}

// API Functions
// API Functions
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: { ...defaultOptions.headers, ...options.headers }
    };
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, finalOptions);
        // Bazı hatalarda boş body olabilir; JSON parse hatasını yutuyoruz
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const err = new Error(data.error || 'An error occurred');
            err.status = response.status; // <<< 409’u yakalamak için
            throw err;
        }
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentication Functions
async function register(userData) {
    try {
        closeModal('registerModal');
        const response = await apiCall('/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        // Otomatik giriş kontrolü
        if (response.access_token) {
            // Otomatik giriş başarılı - token'ı kaydet ve kullanıcıyı giriş yapmış durumda tut
            localStorage.setItem('token', response.access_token);
            localStorage.setItem('user_id', response.user_id);
            
            // UI'yi güncelle
            elements.authButtons.style.display = 'none';
            elements.userProfile.style.display = 'flex';
            elements.userName.textContent = 'Loading...';
            elements.sidebar.style.display = 'flex';
            
            // Kullanıcı profilini ve sohbetleri yükle
            clearChat();
            Promise.all([
                loadUserProfile(),
                loadConversations()
            ]).catch(error => {
                console.error('Background loading error:', error);
            });
        }
        return response;
    } catch (error) {
        showError(error.message);
        throw error;
    }
}
async function login(email, password) {
    try {
        closeModal('loginModal');
        elements.authButtons.style.display = 'none';
        elements.userProfile.style.display = 'flex';
        elements.userName.textContent = 'Loading...';
        elements.sidebar.style.display = 'flex';
        const response = await apiCall('/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('user_id', response.user_id);
        clearChat();
        Promise.all([
            loadUserProfile(),
            loadConversations()
        ]).catch(error => {
            console.error('Background loading error:', error);
        });
        return response;
    } catch (error) {
        elements.authButtons.style.display = 'flex';
        elements.userProfile.style.display = 'none';
        elements.sidebar.style.display = 'none';
        showError(error.message);
        throw error;
    }
}
async function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    currentUser = null;
    currentConversationId = null;
    conversations = [];
    messages = [];
    updateAuthUI();
    clearChat();
    clearConversations();
}
async function loadUserProfile() {
    try {
        const user = await apiCall('/me');
        currentUser = user;
        updateAuthUI();
    } catch (error) {
        console.error('Failed to load user profile:', error);
        logout();
    }
}

// UI Update Functions
function updateAuthUI() {
    if (currentUser) {
        elements.authButtons.style.display = 'none';
        elements.userProfile.style.display = 'flex';
        
        // Safely handle name display with fallbacks
        const firstName = currentUser.first_name || '';
        const lastName = currentUser.last_name || '';
        const displayName = `${firstName} ${lastName}`.trim() || 'User';
        
        elements.userName.textContent = displayName;
        elements.sidebar.style.display = 'flex';
    } else {
        elements.authButtons.style.display = 'flex';
        elements.userProfile.style.display = 'none';
        elements.sidebar.style.display = 'none';
    }
}
function clearChat() {
    elements.welcomeMessage.style.display = 'flex';
    elements.messagesContainer.style.display = 'none';
    elements.messagesContainer.innerHTML = '';
    messages = [];
    currentConversationId = null;
}
function clearConversations() {
    elements.conversationsList.innerHTML = '';
    conversations = [];
}

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
}
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
}

// Profile Modal Functions
async function openProfileModal() {
    try {
        const user = await apiCall('/me'); // GET profile
        currentUser = user; // UI senkronu için güncelle
        elements.pfFirstName.value = user.first_name || '';
        elements.pfLastName.value = user.last_name || '';
        elements.pfEmail.value = user.email || '';
        elements.pfBirthdate.value = formatBirthdateForInput(user.birthdate);
        
        // Update age display
        if (user.birthdate) {
            const age = calculateAge(user.birthdate);
            if (age !== null) {
                elements.pfAgeDisplay.textContent = `Age: ${age} years old`;
            } else {
                elements.pfAgeDisplay.textContent = '';
            }
        } else {
            elements.pfAgeDisplay.textContent = '';
        }
        
        if (elements.pfGender) elements.pfGender.value = (user.gender || '').toLowerCase();
        if (elements.pfCity) elements.pfCity.value = user.city || '';
        openModal('profileModal');
    } catch (err) {
        showError(err.message || 'Failed to load profile.');
    }
}

// Conversation Functions
async function loadConversations() {
    try {
        const response = await apiCall('/conversations');
        conversations = response.conversations;
        renderConversations();
    } catch (error) {
        console.error('Failed to load conversations:', error);
    }
}
function renderConversations() {
    elements.conversationsList.innerHTML = '';
    conversations.forEach(conversation => {
        const conversationElement = document.createElement('div');
        conversationElement.className = 'conversation-item';
        conversationElement.dataset.id = conversation.id;
        conversationElement.innerHTML = `
            <div class="conversation-title">${conversation.title}</div>
            <div class="conversation-date">${formatDate(conversation.created_at)}</div>
            <button class="action-menu-btn" title="Options" aria-label="Options">
                <i class="fas fa-ellipsis-vertical"></i>
            </button>
            <div class="context-menu" role="menu">
                <button class="rename-action" role="menuitem"><i class="fas fa-pen"></i> Yeniden Adlandır</button>
                <button class="delete-action danger" role="menuitem"><i class="fas fa-trash"></i> Sil</button>
            </div>
        `;
        conversationElement.addEventListener('click', (e) => {
            const isAction = e.target.closest('.action-menu-btn, .context-menu');
            if (isAction) return;
            loadConversation(conversation.id);
        });
        const menuBtn = conversationElement.querySelector('.action-menu-btn');
        const menu = conversationElement.querySelector('.context-menu');
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.context-menu.show').forEach(m => m.classList.remove('show'));
            menu.classList.toggle('show');
        });
        document.addEventListener('click', (e) => {
            if (!conversationElement.contains(e.target)) {
                menu.classList.remove('show');
            }
        });
        const renameBtn = conversationElement.querySelector('.rename-action');
        renameBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            menu.classList.remove('show');
            const currentTitle = conversation.title || '';
            openInput({
                title: 'Başlığı düzenle',
                label: 'Yeni başlığı girin:',
                placeholder: 'Yeni başlık',
                value: currentTitle,
                onSubmit: async (val) => {
                    const trimmed = val.trim();
                    if (!trimmed || trimmed === currentTitle) return;
                    try {
                        const resp = await apiCall(`/conversations/${conversation.id}`, {
                            method: 'PATCH',
                            body: JSON.stringify({ title: trimmed })
                        });
                        const idx = conversations.findIndex(c => c.id === conversation.id);
                        if (idx >= 0) conversations[idx].title = resp.title || trimmed;
                        renderConversations();
                    } catch (error) {
                        showError('Başlık güncellenemedi.');
                    }
                }
            });
        });
        const deleteBtn = conversationElement.querySelector('.delete-action');
        deleteBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            menu.classList.remove('show');
            openConfirm({
                title: 'Sohbet silinsin mi?',
                text: 'Bu sohbet ve tüm mesajları kalıcı olarak silinecek.',
                onConfirm: async () => {
                    try {
                        await apiCall(`/conversations/${conversation.id}`, { method: 'DELETE' });
                        conversations = conversations.filter(c => c.id !== conversation.id);
                        if (currentConversationId === conversation.id) {
                            clearChat();
                        }
                        renderConversations();
                    } catch (error) {
                        showError('Sohbet silinemedi. Lütfen tekrar deneyin.');
                    }
                }
            });
        });
        elements.conversationsList.appendChild(conversationElement);
    });
}
async function loadConversation(conversationId) {
    try {
        showLoading();
        const response = await apiCall(`/conversations/${conversationId}/history`);
        currentConversationId = conversationId;
        messages = response.history;
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-id="${conversationId}"]`)?.classList.add('active');
        renderMessages();
        hideLoading();
    } catch (error) {
        console.error('Failed to load conversation:', error);
        hideLoading();
    }
}
function renderMessages() {
    elements.welcomeMessage.style.display = 'none';
    elements.messagesContainer.style.display = 'flex';
    elements.messagesContainer.innerHTML = '';
    messages.forEach(message => {
        addMessageToUI(message.message, message.role);
    });
    scrollToBottom();
}
function addMessageToUI(content, role) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${role}`;
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    if (role === 'assistant') {
        messageContent.innerHTML = parseMarkdown(content);
        // Apply syntax highlighting to code blocks
        if (window.Prism) {
            messageContent.querySelectorAll('pre code').forEach((block) => {
                Prism.highlightElement(block);
            });
        }
    } else {
        messageContent.textContent = content;
    }
    messageElement.appendChild(messageContent);
    elements.messagesContainer.appendChild(messageElement);
    scrollToBottom();
}
// Enhanced markdown parser for assistant messages using marked.js
function parseMarkdown(text) {
    // Configure marked options for better security and rendering
    marked.setOptions({
        breaks: true, // Convert line breaks to <br>
        gfm: true, // GitHub Flavored Markdown
        sanitize: false, // Allow HTML (marked 4.x doesn't use this option)
        smartLists: true,
        smartypants: true,
        highlight: function(code, lang) {
            // Use Prism.js for syntax highlighting
            if (window.Prism && lang) {
                try {
                    return Prism.highlight(code, Prism.languages[lang] || Prism.languages.plaintext, lang);
                } catch (e) {
                    console.warn('Prism highlighting failed:', e);
                }
            }
            return code;
        }
    });
    
    try {
        // Parse markdown to HTML
        const html = marked.parse(text);
        return html;
    } catch (error) {
        console.error('Markdown parsing error:', error);
        // Fallback to basic HTML escaping if parsing fails
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/\n/g, '<br>');
    }
}
function scrollToBottom() {
    const chatContainer = elements.chatContainer;
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Chat Functions
// Chat Functions
async function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message) return;

    // >>> ADD: aktif istek kontrolü
    if (isSending) {
        showToast('Önceki yanıt hazırlanıyor. Lütfen bekleyin.', 'info', { duration: 2000 });
        return;
    }

    isSending = true;
    setInputDisabled(true);

    elements.welcomeMessage.style.display = 'none';
    elements.messagesContainer.style.display = 'flex';
    addMessageToUI(message, 'user');
    elements.messageInput.value = '';
    showTypingIndicator();

    try {
        const requestBody = { prompt: message };
        if (currentConversationId) requestBody.conversation_id = currentConversationId;

        const response = await apiCall('/chat', {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });

        hideTypingIndicator();
        addMessageToUI(response.response, 'assistant');

        if (!currentConversationId) {
            currentConversationId = response.conversation_id;
            await loadConversations();
        }
    } catch (error) {
        hideTypingIndicator();

        if (error.status === 409) {
            // Backend lock 409 dönerse kullanıcıya bilgi ver
            showToast('Yanıt hazırlanıyor. Birkaç saniye sonra tekrar deneyin.', 'info', { duration: 2500 });
        } else {
            console.error('Failed to send message:', error);
            showError('Failed to send message. Please try again.');
        }
    } finally {
        isSending = false;
        setInputDisabled(false);
        elements.messageInput.focus();
    }
}

// Typing indicator functions
function showTypingIndicator() {
    const typingElement = document.createElement('div');
    typingElement.className = 'message assistant typing-indicator';
    typingElement.id = 'typingIndicator';
    const typingContent = document.createElement('div');
    typingContent.className = 'message-content typing-content';
    typingContent.innerHTML = '<span class="typing-dots"><span></span><span></span><span></span></span>';
    typingElement.appendChild(typingContent);
    elements.messagesContainer.appendChild(typingElement);
    scrollToBottom();
}
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) typingIndicator.remove();
}
function startNewChat() {
    clearChat();
    currentConversationId = null;
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    const textarea = elements.messageInput;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Apply saved theme immediately
    applySavedThemePreference();

    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
        loadUserProfile();
        loadConversations();
    } else {
        updateAuthUI();
    }

    // Account modal open/close
    elements.openAccountBtn?.addEventListener('click', () => openModal('accountModal'));
    elements.closeAccountModal?.addEventListener('click', () => closeModal('accountModal'));

// Change Email
    elements.emailForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const newEmail = elements.newEmail.value.trim();
        const pwd = elements.emailPassword?.value || null;

        if (!newEmail) {
            showError('Please enter a new email.');
            return;
        }
        try {
            await apiCall('/me/email', {
                method: 'PATCH',
                body: JSON.stringify({ new_email: newEmail, password: pwd })
            });
            showSuccess('Email updated.');
            closeModal('accountModal');
            // Profili tazele
            await loadUserProfile();
        } catch (err) {
            showError(err.message || 'Email update failed.');
        }
    });

// Change Password
    elements.passwordForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const currentPwd = elements.currentPassword.value;
        const newPwd = elements.newPassword.value;

        if (!currentPwd || !newPwd) {
            showError('Please fill all password fields.');
            return;
        }
        
        const passwordValidation = validatePassword(newPwd);
        if (!passwordValidation.valid) {
            showError(passwordValidation.message);
            return;
        }
        
        try {
            await apiCall('/me/password', {
                method: 'PATCH',
                body: JSON.stringify({ current_password: currentPwd, new_password: newPwd })
            });
            showSuccess('Password updated.');
            closeModal('accountModal');
        } catch (err) {
            showError(err.message || 'Password update failed.');
        }
    });


    // Auth button listeners
    elements.loginBtn?.addEventListener('click', () => openModal('loginModal'));
    elements.registerBtn?.addEventListener('click', () => openModal('registerModal'));
    elements.logoutBtn?.addEventListener('click', logout);

    // Modal close listeners
    elements.closeLoginModal?.addEventListener('click', () => closeModal('loginModal'));
    elements.closeRegisterModal?.addEventListener('click', () => closeModal('registerModal'));
    elements.closeProfileModal?.addEventListener('click', () => closeModal('profileModal'));

    // Make username clickable to open profile
    elements.userName?.addEventListener('click', openProfileModal);

    // === Profile Save (PATCH /me) ===
    elements.profileForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const birthdate = elements.pfBirthdate?.value;
        if (birthdate) {
            const birthdateValidation = validateBirthdate(birthdate);
            if (!birthdateValidation.valid) {
                showError(birthdateValidation.message);
                return;
            }
        }
        
        try {
            const body = {
                first_name: elements.pfFirstName?.value.trim(),
                last_name: elements.pfLastName?.value.trim(),
                birthdate: birthdate || null,
                gender: elements.pfGender ? elements.pfGender.value.trim() : undefined,
                city: elements.pfCity ? elements.pfCity.value.trim() : undefined, // varsa
            };
            Object.keys(body).forEach(k => (body[k] === '' || body[k] === undefined || body[k] === null) && delete body[k]);
            const response = await apiCall('/me', {
                method: 'PATCH',
                body: JSON.stringify(body)
            });
            
            // The backend returns {message: "...", profile: {...}}
            // We need to use the profile data, not the entire response
            if (response.profile) {
                currentUser = response.profile;
            } else {
                // Fallback: reload the full user profile
                const user = await apiCall('/me');
                currentUser = user;
            }
            
            updateAuthUI();
            showSuccess('Profile updated.');
            closeModal('profileModal');
        } catch (err) {
            showError(err.message || 'Profile update failed.');
        }
    });

    // === Profile Cancel ===
    elements.profileCancelBtn?.addEventListener('click', () => closeModal('profileModal'));

    // === Profile Delete (DELETE /me) ===
    elements.profileDeleteBtn?.addEventListener('click', () => {
        openConfirm({
            title: 'Delete account?',
            text: 'Your profile record will be permanently deleted. (Your auth account may not be deleted.)',
            onConfirm: async () => {
                try {
                    await apiCall('/me', { method: 'DELETE' });
                    closeModal('profileModal');
                    showSuccess('Account deleted.');
                    await logout();
                } catch (err) {
                    showError(err.message || 'Delete failed.');
                }
            }
        });
    });

    // Form submissions
    elements.loginForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        try { await login(email, password); } catch {}
    });
    elements.registerForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const birthdate = document.getElementById('registerBirthdate').value;
        const birthdateValidation = validateBirthdate(birthdate);
        
        if (!birthdateValidation.valid) {
            showError(birthdateValidation.message);
            return;
        }
        
        const password = document.getElementById('registerPassword').value;
        const passwordValidation = validatePassword(password);
        
        if (!passwordValidation.valid) {
            showError(passwordValidation.message);
            return;
        }
        
        const userData = {
            email: document.getElementById('registerEmail').value,
            password: password,
            first_name: document.getElementById('registerFirstName').value,
            last_name: document.getElementById('registerLastName').value,
            birthdate: birthdate,
            gender: document.getElementById('registerGender').value
            // city alanını kaldırmıştık
        };
        try { await register(userData); } catch {}
    });

    // Chat listeners
    elements.newChatBtn?.addEventListener('click', startNewChat);
    elements.sendBtn?.addEventListener('click', sendMessage);
    elements.themeToggleBtn?.addEventListener('click', toggleTheme);

    // Enter key to send message
    // Enter key to send message
    elements.messageInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();

            if (isSending) {
                showToast('Önceki yanıt hazırlanıyor…', 'info', { duration: 1500 });
                return;
            }
            sendMessage();
        }
    });

    // Auto-resize textarea
    elements.messageInput?.addEventListener('input', autoResizeTextarea);

    // Update age display when birthdate changes
    elements.pfBirthdate?.addEventListener('change', (e) => {
        const birthdate = e.target.value;
        if (birthdate) {
            const age = calculateAge(birthdate);
            if (age !== null) {
                elements.pfAgeDisplay.textContent = `Age: ${age} years old`;
            } else {
                elements.pfAgeDisplay.textContent = '';
            }
        } else {
            elements.pfAgeDisplay.textContent = '';
        }
    });

    // Real-time password validation
    document.getElementById('registerPassword')?.addEventListener('input', (e) => {
        const password = e.target.value;
        const requirements = document.getElementById('passwordRequirements');
        
        if (password.length > 0) {
            requirements.style.display = 'block';
            const validation = validatePassword(password);
            if (validation.valid) {
                requirements.style.color = '#2f9e44';
                requirements.textContent = '✓ Password meets requirements';
            } else {
                requirements.style.color = '#e03131';
                requirements.textContent = validation.message;
            }
        } else {
            requirements.style.display = 'none';
        }
    });

    document.getElementById('newPassword')?.addEventListener('input', (e) => {
        const password = e.target.value;
        const requirements = document.getElementById('newPasswordRequirements');
        
        if (password.length > 0) {
            requirements.style.display = 'block';
            const validation = validatePassword(password);
            if (validation.valid) {
                requirements.style.color = '#2f9e44';
                requirements.textContent = '✓ Password meets requirements';
            } else {
                requirements.style.color = '#e03131';
                requirements.textContent = validation.message;
            }
        } else {
            requirements.style.display = 'none';
        }
    });

    // Click outside modal to close
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('show');
        }
    });

    // Confirm modal actions
    elements.confirmCancelBtn?.addEventListener('click', closeConfirm);
    elements.confirmDeleteBtn?.addEventListener('click', () => {
        const action = pendingConfirm?.onConfirm;
        closeConfirm();
        if (typeof action === 'function') action();
    });
    elements.confirmModal?.addEventListener('click', (e) => {
        if (e.target.classList.contains('confirm-backdrop')) {
            closeConfirm();
        }
    });

    // Input modal actions
    elements.inputCancelBtn?.addEventListener('click', closeInput);
    elements.inputOkBtn?.addEventListener('click', () => {
        const action = pendingInput?.onSubmit;
        const value = elements.inputField.value;
        closeInput();
        if (typeof action === 'function') action(value);
    });
    elements.inputModal?.addEventListener('click', (e) => {
        if (e.target.classList.contains('confirm-backdrop')) {
            closeInput();
        }
    });
    elements.inputField?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            elements.inputOkBtn.click();
        }
    });
});

// Health check on startup
async function checkServerHealth() {
    try {
        await apiCall('/health');
        console.log('Server is healthy');
    } catch (error) {
        console.error('Server health check failed:', error);
        showError('Unable to connect to server. Please check if the backend is running.');
    }
}
checkServerHealth();