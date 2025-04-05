document.addEventListener("DOMContentLoaded", function() {
    // Call the function to show the first section when the page loads
    showContent(null, 'manage-courses'); // Replace 'progress-container' with the ID of your first div
});

function showContent(event, contentId) {
    if (event) {
        event.preventDefault(); // Prevent default only when triggered by a user event
    }

    // Hide all content sections
    const allSections = document.querySelectorAll('.manage-courses, .manage-students, .manage-assesments');
    allSections.forEach(function(section) {
        section.style.display = 'none'; // Hide all sections
    });

    // Show the clicked or default section
    const activeSection = document.getElementById(contentId);
    if (activeSection) {
        activeSection.style.display = 'block'; // Show the active section
    }
}

