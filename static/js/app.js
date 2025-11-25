// PromptSense Frontend JavaScript

class PromptSenseApp {
    constructor() {
        this.apiBase = '';
        this.currentUserId = 1;
        this.initializeElements();
        this.attachEventListeners();
        this.loadUsers();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.userSelect = document.getElementById('userSelect');
        this.insightsBtn = document.getElementById('insightsBtn');
        this.insightsModal = document.getElementById('insightsModal');
        this.closeModal = document.getElementById('closeModal');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.statusText = document.getElementById('statusText');
    }

    attachEventListeners() {
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });

        // User selection
        this.userSelect.addEventListener('change', (e) => {
            this.currentUserId = parseInt(e.target.value);
            this.updateStatus(`Switched to ${e.target.options[e.target.selectedIndex].text}`);
        });

        // Insights modal
        this.insightsBtn.addEventListener('click', () => this.showInsights());
        this.closeModal.addEventListener('click', () => this.hideInsights());
        this.insightsModal.addEventListener('click', (e) => {
            if (e.target === this.insightsModal) {
                this.hideInsights();
            }
        });
    }

    async loadUsers() {
        try {
            const response = await fetch(`${this.apiBase}/api/users`);
            const data = await response.json();

            if (data.success && data.users.length > 0) {
                this.userSelect.innerHTML = '';
                data.users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    const level = user.preferences.expertise_level || 'intermediate';
                    option.textContent = `${user.name} (${level})`;
                    this.userSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();

        if (!message) {
            return;
        }

        // Disable input
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
        this.updateStatus('Sending...');

        // Add user message to chat
        this.addMessage('user', message);

        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        // Show typing indicator
        this.showTyping();

        try {
            const response = await fetch(`${this.apiBase}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.currentUserId
                })
            });

            const data = await response.json();

            // Hide typing indicator
            this.hideTyping();

            if (data.success) {
                // Add assistant message
                this.addMessage('assistant', data.response, data.metadata);
                this.updateStatus('Ready');
            } else {
                this.addMessage('assistant', 'Sorry, I encountered an error: ' + (data.error || 'Unknown error'));
                this.updateStatus('Error occurred');
            }
        } catch (error) {
            this.hideTyping();
            console.error('Error sending message:', error);
            this.addMessage('assistant', 'Sorry, I couldn\'t connect to the server. Please try again.');
            this.updateStatus('Connection error');
        } finally {
            // Re-enable input
            this.messageInput.disabled = false;
            this.sendBtn.disabled = false;
            this.messageInput.focus();
        }
    }

    addMessage(role, content, metadata = null) {
        // Remove welcome message if present
        const welcomeMsg = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? '👤' : '🤖';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        const text = document.createElement('div');
        text.className = 'message-text';
        text.textContent = content;

        bubble.appendChild(text);

        // Add metadata for assistant messages
        if (role === 'assistant' && metadata) {
            const metadataDiv = document.createElement('div');
            metadataDiv.className = 'message-metadata';

            const metadataRow = document.createElement('div');
            metadataRow.className = 'metadata-row';

            if (metadata.intent) {
                const intentBadge = document.createElement('span');
                intentBadge.className = 'metadata-badge';
                intentBadge.textContent = `Intent: ${metadata.intent}`;
                metadataRow.appendChild(intentBadge);
            }

            if (metadata.domain) {
                const domainBadge = document.createElement('span');
                domainBadge.className = 'metadata-badge';
                domainBadge.textContent = `Domain: ${metadata.domain}`;
                metadataRow.appendChild(domainBadge);
            }

            if (metadata.similar_queries && metadata.similar_queries.length > 0) {
                const similarBadge = document.createElement('span');
                similarBadge.className = 'metadata-badge';
                similarBadge.textContent = `${metadata.similar_queries.length} similar queries found`;
                metadataRow.appendChild(similarBadge);
            }

            metadataDiv.appendChild(metadataRow);
            bubble.appendChild(metadataDiv);
        }

        messageContent.appendChild(bubble);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTyping() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTyping() {
        this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    updateStatus(text) {
        this.statusText.textContent = text;
        setTimeout(() => {
            if (this.statusText.textContent === text) {
                this.statusText.textContent = 'Ready';
            }
        }, 3000);
    }

    async showInsights() {
        this.insightsModal.classList.add('active');
        const content = document.getElementById('insightsContent');
        content.innerHTML = '<div class="loading">Loading insights...</div>';

        try {
            const response = await fetch(`${this.apiBase}/api/chat/insights/${this.currentUserId}`);
            const data = await response.json();

            if (data.success) {
                content.innerHTML = this.renderInsights(data.insights);
            } else {
                content.innerHTML = '<p>Error loading insights.</p>';
            }
        } catch (error) {
            console.error('Error loading insights:', error);
            content.innerHTML = '<p>Error loading insights.</p>';
        }
    }

    renderInsights(insights) {
        let html = '<div class="insight-section">';
        html += '<h3>Conversation Statistics</h3>';
        html += '<div class="insight-grid">';

        html += `
            <div class="insight-card">
                <div class="insight-value">${insights.total_messages || 0}</div>
                <div class="insight-label">Total Messages</div>
            </div>
            <div class="insight-card">
                <div class="insight-value">${insights.faiss_vectors || 0}</div>
                <div class="insight-label">Indexed Queries</div>
            </div>
        `;

        html += '</div></div>';

        if (insights.common_domains && insights.common_domains.length > 0) {
            html += '<div class="insight-section">';
            html += '<h3>Common Domains</h3>';
            html += '<div class="insight-grid">';

            insights.common_domains.slice(0, 4).forEach(domain => {
                html += `
                    <div class="insight-card">
                        <div class="insight-value">${this.getDomainEmoji(domain)}</div>
                        <div class="insight-label">${domain}</div>
                    </div>
                `;
            });

            html += '</div></div>';
        }

        if (insights.common_intents && Object.keys(insights.common_intents).length > 0) {
            html += '<div class="insight-section">';
            html += '<h3>Common Intents</h3>';
            html += '<div class="insight-grid">';

            Object.entries(insights.common_intents).slice(0, 4).forEach(([intent, count]) => {
                html += `
                    <div class="insight-card">
                        <div class="insight-value">${count}</div>
                        <div class="insight-label">${intent}</div>
                    </div>
                `;
            });

            html += '</div></div>';
        }

        return html;
    }

    getDomainEmoji(domain) {
        const emojis = {
            'technology': '💻',
            'science': '🔬',
            'business': '💼',
            'creative': '🎨',
            'education': '📚',
            'health': '🏥',
            'travel': '✈️',
            'general': '💬'
        };
        return emojis[domain] || '📝';
    }

    hideInsights() {
        this.insightsModal.classList.remove('active');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PromptSenseApp();
});
