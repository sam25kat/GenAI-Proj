// PromptSense Frontend JavaScript

class PromptSenseApp {
    constructor() {
        this.apiBase = '';
        this.currentUserId = 1;
        this.currentConversationId = null;
        this.initializeElements();
        this.attachEventListeners();
        this.loadUsers();
        this.loadConversations();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.insightsBtn = document.getElementById('insightsBtn');
        this.insightsModal = document.getElementById('insightsModal');
        this.closeModal = document.getElementById('closeModal');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsModal = document.getElementById('settingsModal');
        this.closeSettingsModal = document.getElementById('closeSettingsModal');
        this.settingsForm = document.getElementById('settingsForm');
        this.cancelSettings = document.getElementById('cancelSettings');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.statusText = document.getElementById('statusText');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.conversationsList = document.getElementById('conversationsList');
        this.toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
        this.mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
        this.sidebar = document.getElementById('sidebar');
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

        // Insights modal
        this.insightsBtn.addEventListener('click', () => this.showInsights());
        this.closeModal.addEventListener('click', () => this.hideInsights());
        this.insightsModal.addEventListener('click', (e) => {
            if (e.target === this.insightsModal) {
                this.hideInsights();
            }
        });

        // Settings modal
        this.settingsBtn.addEventListener('click', () => this.showSettings());
        this.closeSettingsModal.addEventListener('click', () => this.hideSettings());
        this.cancelSettings.addEventListener('click', () => this.hideSettings());
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.hideSettings();
            }
        });
        this.settingsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });

        // New chat button
        this.newChatBtn.addEventListener('click', () => this.createNewChat());

        // Sidebar toggle (mobile)
        if (this.toggleSidebarBtn) {
            this.toggleSidebarBtn.addEventListener('click', () => this.toggleSidebar());
        }
        if (this.mobileSidebarToggle) {
            this.mobileSidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
    }

    async loadUsers() {
        // User selection removed - defaulting to user ID 1
        // This method is kept for backward compatibility but does nothing
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
                    user_id: this.currentUserId,
                    conversation_id: this.currentConversationId
                })
            });

            const data = await response.json();

            // Hide typing indicator
            this.hideTyping();

            if (data.success) {
                // Add assistant message with enhanced prompt
                this.addMessage('assistant', data.response, data.metadata, data.enhanced_prompt);
                this.updateStatus('Ready');

                // Update conversation ID if it's a new conversation
                if (data.conversation_id && !this.currentConversationId) {
                    this.currentConversationId = data.conversation_id;
                    // Generate title for new conversation after first message
                    this.generateConversationTitle(this.currentConversationId, message);
                }

                // Reload conversations list to update
                this.loadConversations();
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

    addMessage(role, content, metadata = null, enhancedPrompt = null) {
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

        // Add enhanced prompt toggle for any message that has an enhanced prompt
        if (enhancedPrompt) {
            const enhancedPromptSection = document.createElement('div');
            enhancedPromptSection.className = 'enhanced-prompt-section';

            const toggleButton = document.createElement('button');
            toggleButton.className = 'enhanced-prompt-toggle';
            toggleButton.textContent = '🔍 View Enhanced Prompt';
            toggleButton.onclick = () => {
                const content = enhancedPromptSection.querySelector('.enhanced-prompt-content');
                const isVisible = content.style.display === 'block';
                content.style.display = isVisible ? 'none' : 'block';
                toggleButton.textContent = isVisible ? '🔍 View Enhanced Prompt' : '🔼 Hide Enhanced Prompt';
            };

            const promptContent = document.createElement('div');
            promptContent.className = 'enhanced-prompt-content';
            promptContent.style.display = 'none';

            const promptLabel = document.createElement('div');
            promptLabel.className = 'enhanced-prompt-label';
            promptLabel.textContent = 'Enhanced Prompt Sent to LLM:';

            const promptText = document.createElement('pre');
            promptText.className = 'enhanced-prompt-text';
            promptText.textContent = enhancedPrompt;

            promptContent.appendChild(promptLabel);
            promptContent.appendChild(promptText);

            enhancedPromptSection.appendChild(toggleButton);
            enhancedPromptSection.appendChild(promptContent);
            bubble.appendChild(enhancedPromptSection);
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

    async showSettings() {
        this.settingsModal.classList.add('active');

        // Load current user preferences
        try {
            const response = await fetch(`${this.apiBase}/api/users/${this.currentUserId}`);
            const data = await response.json();

            if (data.success && data.user) {
                const prefs = data.user.preferences || {};

                // Set expertise level
                const expertiseLevel = prefs.expertise_level || 'intermediate';
                const expertiseRadio = document.querySelector(`input[name="expertise_level"][value="${expertiseLevel}"]`);
                if (expertiseRadio) expertiseRadio.checked = true;

                // Set tone
                const tone = prefs.tone || 'professional';
                const toneRadio = document.querySelector(`input[name="tone"][value="${tone}"]`);
                if (toneRadio) toneRadio.checked = true;

                // Set custom instructions
                const customInstructions = prefs.custom_instructions || '';
                document.getElementById('customInstructions').value = customInstructions;
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    hideSettings() {
        this.settingsModal.classList.remove('active');
    }

    async saveSettings() {
        try {
            const formData = new FormData(this.settingsForm);

            const preferences = {
                expertise_level: formData.get('expertise_level'),
                tone: formData.get('tone'),
                custom_instructions: formData.get('custom_instructions')
            };

            this.updateStatus('Saving preferences...');

            const response = await fetch(`${this.apiBase}/api/users/${this.currentUserId}/preferences`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preferences)
            });

            const data = await response.json();

            if (data.success) {
                this.updateStatus('Preferences saved!');
                this.hideSettings();
            } else {
                this.updateStatus('Error saving preferences');
                alert('Failed to save preferences: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            this.updateStatus('Error saving preferences');
            alert('Failed to save preferences. Please try again.');
        }
    }

    async loadConversations() {
        try {
            const response = await fetch(`${this.apiBase}/api/conversations/${this.currentUserId}`);
            const data = await response.json();

            if (data.success && data.conversations) {
                this.renderConversations(data.conversations);
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
            this.conversationsList.innerHTML = '<div class="loading-conversations">Error loading conversations</div>';
        }
    }

    renderConversations(conversations) {
        if (conversations.length === 0) {
            this.conversationsList.innerHTML = '<div class="loading-conversations">No conversations yet. Click "+ New Chat" to start!</div>';
            return;
        }

        this.conversationsList.innerHTML = '';

        conversations.forEach(conversation => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            if (conversation.id === this.currentConversationId) {
                item.classList.add('active');
            }

            const title = document.createElement('div');
            title.className = 'conversation-title';
            title.textContent = conversation.title || 'New Conversation';

            // Auto-generate title for conversations with generic names
            const isGenericTitle = conversation.title === 'New Conversation' ||
                                  conversation.title === 'Previous Conversation';
            if (isGenericTitle) {
                this.generateConversationTitleIfNeeded(conversation.id);
            }

            const date = document.createElement('div');
            date.className = 'conversation-date';
            date.textContent = this.formatDate(conversation.updated_at || conversation.created_at);

            const actions = document.createElement('div');
            actions.className = 'conversation-actions';

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn-delete-conversation';
            deleteBtn.textContent = 'Delete';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                this.deleteConversation(conversation.id);
            };

            actions.appendChild(deleteBtn);

            item.appendChild(title);
            item.appendChild(date);
            item.appendChild(actions);

            item.onclick = () => this.loadConversation(conversation.id);

            this.conversationsList.appendChild(item);
        });
    }

    async createNewChat() {
        try {
            this.updateStatus('Creating new chat...');

            const response = await fetch(`${this.apiBase}/api/conversations/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.currentUserId,
                    title: 'New Conversation'
                })
            });

            const data = await response.json();

            if (data.success && data.conversation_id) {
                this.currentConversationId = data.conversation_id;
                this.clearChat();
                this.loadConversations();
                this.updateStatus('New chat created');
                this.messageInput.focus();
            } else {
                this.updateStatus('Error creating chat');
            }
        } catch (error) {
            console.error('Error creating new chat:', error);
            this.updateStatus('Error creating chat');
        }
    }

    async loadConversation(conversationId) {
        try {
            this.updateStatus('Loading conversation...');

            const response = await fetch(`${this.apiBase}/api/conversations/${conversationId}/messages`);
            const data = await response.json();

            if (data.success && data.messages) {
                this.currentConversationId = conversationId;
                this.clearChat();

                // Add all messages from the conversation
                data.messages.forEach(msg => {
                    if (msg.role === 'user') {
                        // User messages also have enhanced prompts
                        const metadata = msg.metadata || {};
                        if (msg.intent) metadata.intent = msg.intent;
                        if (msg.domain) metadata.domain = msg.domain;
                        this.addMessage('user', msg.content, metadata, msg.enhanced_prompt);
                    } else if (msg.role === 'assistant') {
                        const metadata = msg.metadata || {};
                        if (msg.intent) metadata.intent = msg.intent;
                        if (msg.domain) metadata.domain = msg.domain;
                        this.addMessage('assistant', msg.content, metadata, msg.enhanced_prompt);
                    }
                });

                this.loadConversations();
                this.updateStatus('Conversation loaded');
            } else {
                this.updateStatus('Error loading conversation');
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
            this.updateStatus('Error loading conversation');
        }
    }

    async deleteConversation(conversationId) {
        if (!confirm('Are you sure you want to delete this conversation?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/api/conversations/${conversationId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                // If we deleted the current conversation, clear the chat
                if (conversationId === this.currentConversationId) {
                    this.currentConversationId = null;
                    this.clearChat();
                }

                this.loadConversations();
                this.updateStatus('Conversation deleted');
            } else {
                this.updateStatus('Error deleting conversation');
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
            this.updateStatus('Error deleting conversation');
        }
    }

    async generateConversationTitle(conversationId, firstMessage) {
        try {
            await fetch(`${this.apiBase}/api/conversations/${conversationId}/generate-title`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: firstMessage
                })
            });

            // Reload conversations to show the new title
            setTimeout(() => this.loadConversations(), 1000);
        } catch (error) {
            console.error('Error generating conversation title:', error);
        }
    }

    async generateConversationTitleIfNeeded(conversationId) {
        // Prevent multiple simultaneous requests for the same conversation
        if (!this.generatingTitles) {
            this.generatingTitles = new Set();
        }

        if (this.generatingTitles.has(conversationId)) {
            return;
        }

        this.generatingTitles.add(conversationId);

        try {
            const response = await fetch(`${this.apiBase}/api/conversations/${conversationId}/generate-title`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            // If conversation doesn't exist (404), stop trying to generate title
            if (response.status === 404) {
                console.warn(`Conversation ${conversationId} not found, skipping title generation`);
                this.generatingTitles.delete(conversationId);
                return;
            }

            // Reload conversations to show the new title after a short delay
            setTimeout(() => {
                this.loadConversations();
                this.generatingTitles.delete(conversationId);
            }, 1000);
        } catch (error) {
            console.error('Error generating conversation title:', error);
            this.generatingTitles.delete(conversationId);
        }
    }

    clearChat() {
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">💬</div>
                <h2>Welcome to PromptSense</h2>
                <p>Your intelligent prompt enhancement assistant</p>
                <ul>
                    <li>Context-aware responses</li>
                    <li>Learning from your history</li>
                    <li>Personalized to your style</li>
                </ul>
                <p class="hint">Start typing your message below to begin!</p>
            </div>
        `;
    }

    toggleSidebar() {
        // On desktop, toggle 'collapsed' class
        // On mobile, toggle 'open' class
        if (window.innerWidth > 768) {
            this.sidebar.classList.toggle('collapsed');
        } else {
            this.sidebar.classList.toggle('open');
        }
    }

    formatDate(dateString) {
        // Parse the date string - PostgreSQL returns timestamps without 'Z' suffix
        // So we need to treat them as UTC by adding 'Z' if not present
        let dateStr = dateString;
        if (!dateStr.endsWith('Z') && !dateStr.includes('+')) {
            dateStr += 'Z';
        }

        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;

        return date.toLocaleDateString();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PromptSenseApp();
});
