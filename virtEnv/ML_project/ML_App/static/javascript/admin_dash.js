document.addEventListener("DOMContentLoaded", function() {
    // Call the function to show the first section when the page loads
    showContent(event, 'manage-instructors'); // Replace 'progress-container' with the ID of your first div
});

function showContent(event, contentId) {
    if (event) {
        event.preventDefault(); // Prevent default only when triggered by a user event
    }

    // Hide all content sections
    const allSections = document.querySelectorAll('.manage-instructors, .manage-users, .manage-students');
    allSections.forEach(function(section) {
        section.style.display = 'none'; // Hide all sections
    });

    // Show the clicked or default section
    const activeSection = document.getElementById(contentId);
    if (activeSection) {
        activeSection.style.display = 'block'; // Show the active section
    }
}

