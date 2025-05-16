/**
 * Dark Mode functionality for the Inventory Management System
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get the dark mode toggle button
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    // Check if dark mode is enabled in localStorage
    const isDarkMode = localStorage.getItem('darkMode') === 'enabled';
    
    // Set initial state
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        updateDarkModeIcon(true);
    }
    
    // Add event listener to the dark mode toggle button
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            // Toggle dark mode
            const isDarkModeEnabled = document.body.classList.toggle('dark-mode');
            
            // Update localStorage
            if (isDarkModeEnabled) {
                localStorage.setItem('darkMode', 'enabled');
            } else {
                localStorage.setItem('darkMode', 'disabled');
            }
            
            // Update the icon
            updateDarkModeIcon(isDarkModeEnabled);
        });
    }
    
    /**
     * Update the dark mode toggle icon based on the current mode
     * @param {boolean} isDarkModeEnabled - Whether dark mode is enabled
     */
    function updateDarkModeIcon(isDarkModeEnabled) {
        if (!darkModeToggle) return;
        
        const iconElement = darkModeToggle.querySelector('i');
        if (!iconElement) return;
        
        if (isDarkModeEnabled) {
            // Change to sun icon for light mode option
            iconElement.classList.remove('fa-moon');
            iconElement.classList.add('fa-sun');
        } else {
            // Change to moon icon for dark mode option
            iconElement.classList.remove('fa-sun');
            iconElement.classList.add('fa-moon');
        }
    }
});
