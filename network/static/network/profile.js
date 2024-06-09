document.addEventListener('DOMContentLoaded', function () {
    const followForm = document.getElementById('followForm');

    if (followForm) {
        followForm.addEventListener('submit', function (event) {
            event.preventDefault();


            const formData = new FormData(followForm);
            const followToggleValue = formData.get('follow_toggle');
            const followButton = followForm.querySelector('input[type="submit"]');
            followButton.disabled = true;
            location.reload();

            fetch(followForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    followButton.value = data.button_text;

                    const isFollowing = data.button_text.toLowerCase() === 'unfollow';

                    followButton.disabled = false;
                    location.reload();
                } else {
                    console.error('Follow/Unfollow request failed');
                }
            })
            .catch(error => {
                console.error('Error during Follow/Unfollow request:', error);
            });
        });
    }
});