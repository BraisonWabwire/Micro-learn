document.addEventListener("DOMContentLoaded", function() {
    // Call the function to show the first section when the page loads
    showContent(event, 'manage-instructors'); // Replace 'manage-instructors' with the ID of your first div
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
        activeSection.style.display = 'flex'; // Set display to flex instead of block
    }
}




// Function to open the overlay
function showOverlay() {
    let overlay = document.getElementById("form-overlay");
    overlay.style.display = "flex";
    overlay.classList.add("show");
}

// Function to close the overlay
function closeOverlay() {
    let overlay = document.getElementById("form-overlay");
    overlay.classList.remove("show");
    setTimeout(() => {
        overlay.style.display = "none";
    }, 300);
}

// Ensure only the intended button triggers the overlay
document.querySelector('.btn-add').addEventListener('click', function (e) {
    e.preventDefault();
    showOverlay(); // Show the overlay
});





// Messages 
document.addEventListener("DOMContentLoaded", function () {
    let alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease-in-out"; // Smooth transition
            alert.style.opacity = "0"; // Start fade-out
            setTimeout(() => alert.remove(), 500); // Remove element after fade-out
        }, 3000); // Message disappears after 3 seconds
    });
});

