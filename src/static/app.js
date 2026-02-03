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
        const template = document.getElementById("activity-card-template");
        const activityCard = template.content.cloneNode(true);

        const spotsLeft = details.max_participants - details.participants.length;

        // Populate card content
        activityCard.querySelector(".activity-title").textContent = name;
        activityCard.querySelector(".activity-desc").textContent = details.description;

        // Add schedule and availability info
        const infoDiv = document.createElement("p");
        infoDiv.innerHTML = `<strong>Schedule:</strong> ${details.schedule}<br><strong>Availability:</strong> ${spotsLeft} spots left`;
        activityCard.querySelector(".activity-desc").after(infoDiv);

        // Populate participants list
        const participantsList = activityCard.querySelector(".participants-list");
        details.participants.forEach((participant) => {
          const li = document.createElement("li");
          const span = document.createElement("span");
          span.textContent = participant;
          li.appendChild(span);

          const deleteBtn = document.createElement("button");
          deleteBtn.className = "delete-btn";
          deleteBtn.innerHTML = "✕";
          deleteBtn.setAttribute("aria-label", `Remove ${participant}`);
          deleteBtn.type = "button";
          deleteBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            await unregisterParticipant(name, participant);
          });
          li.appendChild(deleteBtn);
          participantsList.appendChild(li);
        });

        // Store activity name for unregister functionality
        activityCard.querySelector(".activity-name").value = name;

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
        // Refresh activities to update the participant list
        await fetchActivities();
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

  // Function to unregister a participant from an activity
  async function unregisterParticipant(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        // Refresh activities to update the list
        await fetchActivities();
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
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  // Make unregisterParticipant accessible in global scope
  window.unregisterParticipant = unregisterParticipant;

  // Initialize app
  fetchActivities();
});
