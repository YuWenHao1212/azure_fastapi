/**
 * Final TinyMCE Marker Toggle Solution for Bubble.io
 * 最終的 TinyMCE 標記切換解決方案
 * 
 * This script provides the working solution for toggling opt-tags visibility
 * in TinyMCE Rich Text Editor within Bubble.io applications.
 * 
 * Usage in Bubble.io:
 * 1. Add this script to your page HTML header
 * 2. Call toggleTinyMCEMarkers(true) to hide markers
 * 3. Call toggleTinyMCEMarkers(false) to show markers
 */

window.TinyMCEMarkerToggle = {
    
    /**
     * Gets the active TinyMCE editor instance
     */
    getActiveEditor: function() {
        try {
            if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
                return tinymce.activeEditor;
            }
        } catch (e) {
            console.warn('Error getting active editor:', e.message);
        }
        return null;
    },

    /**
     * Injects the CSS styles needed for marker visibility
     * This is crucial because markers have no default styling in Bubble.io
     */
    injectMarkerStyles: function(iframeDoc) {
        try {
            // Remove existing styles first to avoid conflicts
            const existing = iframeDoc.getElementById('bubble-marker-styles');
            if (existing) existing.remove();
            
            const style = iframeDoc.createElement('style');
            style.id = 'bubble-marker-styles';
            style.textContent = `
                /* Default visible styles for opt-tags */
                .opt-new {
                    background-color: rgba(16, 185, 129, 0.1) !important;
                    border-left: 4px solid #10B981 !important;
                    padding-left: 16px !important;
                    margin: 4px 0 !important;
                }
                
                .opt-modified {
                    background-color: #fef3c7 !important;
                    padding: 2px 6px !important;
                    border-radius: 3px !important;
                }
                
                .opt-placeholder {
                    background-color: #fee2e2 !important;
                    color: #991b1b !important;
                    border: 1px dashed #f87171 !important;
                    padding: 2px 8px !important;
                    border-radius: 4px !important;
                    font-style: italic !important;
                }
                
                .opt-keyword {
                    background-color: transparent !important;
                    color: #6366f1 !important;
                    border: 1px solid #c7d2fe !important;
                    padding: 2px 6px !important;
                    border-radius: 3px !important;
                    font-weight: 500 !important;
                }
                
                .opt-keyword-existing {
                    background-color: #2563eb !important;
                    color: white !important;
                    padding: 3px 8px !important;
                    border-radius: 4px !important;
                    font-weight: 600 !important;
                }
                
                /* Hide styles when toggle is active */
                .hide-all-tags .opt-new {
                    background-color: transparent !important;
                    border-left: none !important;
                    padding: 0 !important;
                    margin: 0 !important;
                }
                
                .hide-all-tags .opt-modified {
                    background-color: transparent !important;
                    padding: 0 !important;
                    border-radius: 0 !important;
                }
                
                .hide-all-tags .opt-placeholder {
                    background-color: transparent !important;
                    color: inherit !important;
                    border: none !important;
                    padding: 0 !important;
                    font-style: normal !important;
                }
                
                .hide-all-tags .opt-keyword {
                    background-color: transparent !important;
                    color: inherit !important;
                    border: none !important;
                    padding: 0 !important;
                    font-weight: normal !important;
                }
                
                .hide-all-tags .opt-keyword-existing {
                    background-color: transparent !important;
                    color: inherit !important;
                    padding: 0 !important;
                    font-weight: normal !important;
                }
            `;
            
            iframeDoc.head.appendChild(style);
            return true;
        } catch (e) {
            console.error('Error injecting marker styles:', e.message);
            return false;
        }
    },

    /**
     * Forces a refresh of the TinyMCE editor to ensure visual changes are applied
     */
    forceRefresh: function(editor, iframeDoc) {
        try {
            const body = iframeDoc.body;
            
            // Strategy 1: Force style recalculation
            body.style.display = 'none';
            body.offsetHeight; // Trigger reflow
            body.style.display = '';
            
            // Strategy 2: Update content to trigger TinyMCE refresh
            if (typeof editor.getContent === 'function' && typeof editor.setContent === 'function') {
                const content = editor.getContent();
                editor.setContent(content);
            }
            
            // Strategy 3: Fire TinyMCE events
            if (typeof editor.fire === 'function') {
                editor.fire('change');
                editor.fire('input');
            }
            
            // Strategy 4: Node change event
            if (typeof editor.nodeChanged === 'function') {
                editor.nodeChanged();
            }
            
            return true;
        } catch (e) {
            console.error('Error forcing refresh:', e.message);
            return false;
        }
    },

    /**
     * Main toggle function - call this from your Bubble.io workflows
     * @param {boolean} hideMarkers - true to hide markers, false to show them
     */
    toggle: function(hideMarkers) {
        console.log(`TinyMCE Marker Toggle: ${hideMarkers ? 'HIDING' : 'SHOWING'} markers`);
        
        try {
            const editor = this.getActiveEditor();
            if (!editor) {
                console.error('No active TinyMCE editor found');
                return false;
            }
            
            if (typeof editor.getDoc !== 'function') {
                console.error('Editor does not have getDoc method');
                return false;
            }
            
            const iframeDoc = editor.getDoc();
            const body = iframeDoc.body;
            
            // Step 1: Always inject styles first (crucial for visibility)
            const stylesInjected = this.injectMarkerStyles(iframeDoc);
            if (!stylesInjected) {
                console.error('Failed to inject marker styles');
                return false;
            }
            
            // Step 2: Toggle the hide class
            if (hideMarkers) {
                body.classList.add('hide-all-tags');
                console.log('Added hide-all-tags class');
            } else {
                body.classList.remove('hide-all-tags');
                console.log('Removed hide-all-tags class');
            }
            
            // Step 3: Force refresh to ensure visual changes
            const refreshed = this.forceRefresh(editor, iframeDoc);
            if (!refreshed) {
                console.warn('Refresh may not have worked properly');
            }
            
            console.log('Marker toggle completed successfully');
            return true;
            
        } catch (error) {
            console.error('Critical error in marker toggle:', error.message);
            return false;
        }
    }
};

/**
 * Main function for Bubble.io integration
 * Use this function in your Bubble.io workflows
 * 
 * @param {boolean} hideMarkers - true to hide all opt-tags, false to show them
 * @returns {boolean} - true if successful, false if failed
 */
window.toggleTinyMCEMarkers = function(hideMarkers) {
    return window.TinyMCEMarkerToggle.toggle(hideMarkers);
};

/**
 * Convenience functions for easier use
 */
window.showTinyMCEMarkers = function() {
    return window.toggleTinyMCEMarkers(false);
};

window.hideTinyMCEMarkers = function() {
    return window.toggleTinyMCEMarkers(true);
};

/**
 * Initialization - auto-inject styles when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('TinyMCE Marker Toggle script loaded');
    
    // Wait for TinyMCE to be ready
    const checkTinyMCE = setInterval(function() {
        if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
            console.log('TinyMCE detected, initializing marker styles');
            
            // Auto-inject styles on first load
            const editor = tinymce.activeEditor;
            if (editor && typeof editor.getDoc === 'function') {
                const iframeDoc = editor.getDoc();
                window.TinyMCEMarkerToggle.injectMarkerStyles(iframeDoc);
                console.log('Initial marker styles injected');
            }
            
            clearInterval(checkTinyMCE);
        }
    }, 1000);
    
    // Clear the interval after 30 seconds if TinyMCE is not found
    setTimeout(() => clearInterval(checkTinyMCE), 30000);
});