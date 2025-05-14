// avatar_preview.js
  
document.addEventListener("DOMContentLoaded", function () {
  const avatarOptions = document.querySelectorAll(".avatar-option");
  const avatarInput = document.getElementById("dicebear-url");

  avatarOptions.forEach(option => {
    option.addEventListener("click", () => {
      // Remove previous selections
      avatarOptions.forEach(opt => opt.classList.remove("selected-avatar"));

      // Highlight current
      option.classList.add("selected-avatar");

      // Set hidden input value
      avatarInput.value = option.dataset.avatarUrl;
    });
  });
});

