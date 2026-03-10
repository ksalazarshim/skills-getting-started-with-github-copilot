document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // build participants bullet list
        let participantsHtml = "<p><strong>Participants:</strong></p>";
        if (details.participants.length > 0) {
          participantsHtml += "<ul class=\"participants-list\">" +
            details.participants
              .map(email => `<li>${email} <span class=\"remove-participant\" data-email=\"${email}\" data-activity=\"${name}\">&times;</span></li>`)
              .join("") +
            "</ul>";
        } else {
          participantsHtml += "<p class=\"info\">No one has signed up yet.</p>";
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // reload activities so new participant shows up immediately
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // handle removal clicks using event delegation
  activitiesList.addEventListener("click", async (event) => {
    if (event.target.classList.contains("remove-participant")) {
      const email = event.target.dataset.email;
      const activity = event.target.dataset.activity;

      try {
        const resp = await fetch(
          `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
          { method: "DELETE" }
        );
        const resJson = await resp.json();
        if (resp.ok) {
          messageDiv.textContent = resJson.message;
          messageDiv.className = "success";
          // refresh list
          fetchActivities();
        } else {
          messageDiv.textContent = resJson.detail || "Unable to remove participant";
          messageDiv.className = "error";
        }
        messageDiv.classList.remove("hidden");
        setTimeout(() => messageDiv.classList.add("hidden"), 5000);
      } catch (err) {
        messageDiv.textContent = "Failed to remove participant.";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        console.error(err);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
