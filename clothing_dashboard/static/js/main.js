document.addEventListener('DOMContentLoaded', function () {
    const passwordField = document.getElementById('passwrd');
    const showPasswordToggle = document.getElementById('showPasswordToggle');
    const showIcon = showPasswordToggle.querySelector('.fa-eye');
    const hideIcon = showPasswordToggle.querySelector('.fa-eye-slash');

    showPasswordToggle.addEventListener('click', function () {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            showIcon.style.display = 'none';
            hideIcon.style.display = 'block';
        } else {
            passwordField.type = 'password';
            showIcon.style.display = 'block';
            hideIcon.style.display = 'none';
        }
    });
});

function displayImage(event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        const imageCard = document.getElementById('imageCard');
        imageCard.innerHTML = `<img src="${e.target.result}" alt="profile_image" class="w-100 border-radius-lg shadow-sm">`;
      };
      reader.readAsDataURL(file);
    }
  }

  /* 1. Proloder */
$(window).on('load', function () {
    $('#preloader-active').delay(450).fadeOut('slow');
    $('body').delay(450).css({
      'overflow': 'visible'
    });
  });
