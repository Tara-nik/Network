document.addEventListener('DOMContentLoaded', () => {
     document.querySelectorAll('.likeButton').forEach(likeButton => {
        likeButton.addEventListener('click', function () {
            const postId = this.dataset.postId;

            likes(postId);
        });
    });


    document.querySelectorAll('.edit-btn').forEach(function (button) {
        button.addEventListener('click', function () {
            editPost(button.dataset.postId);
            console.log(`detaset: ${button.dataset.postId}`)
        });
    });
});

function likes(postid) {
    console.log(`postid: ${postid}`);

    let like = document.querySelector(`.likeButton[data-post-id="${postid}"]`);
    console.log(`like element:`, like);

    let likesNumber = document.querySelector(`.l_num[data-post-id="${postid}"]`);
    console.log(`likesNumber element:`, likesNumber);

    if (like && likesNumber) {
        if (like.classList.contains('added')) {
            fetch(`/like_post/${postid}/`, {
                method: 'POST',
                body: JSON.stringify({
                    like: false
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to unlike post');
                    }
                    console.log("Unliked successfully");
                    likesNumber.textContent--;
                })
                .catch(error => {
                    console.error('An error occurred:', error);
                });
        } else {
            fetch(`/like_post/${postid}/`, {
                method: 'POST',
                body: JSON.stringify({
                    like: true
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to like post');
                    }
                    console.log("Liked successfully");
                    likesNumber.textContent++;
                })
                .catch(error => {
                    console.error('An error occurred:', error);
                });
        }

        like.classList.toggle('added');
    }
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function editPost(postId) {
    var postContent = document.getElementById('post-content-' + postId);
    if (postContent) {
        postContent.style.display = 'none';

        var editForm = document.getElementById('edit-form-' + postId);
        if (editForm) {
            editForm.style.display = 'block';
        }
    }
}

function cancelEdit(postId) {
    var postContent = document.getElementById('post-content-' + postId);
    postContent.style.display = 'block';

    var editForm = document.getElementById('edit-form-' + postId);
    if (editForm) {
        editForm.style.display = 'none';
    }
}

function submitForm(postId) {
    var form = document.getElementById('form-' + postId);
    var formData = new FormData(form);

    fetch(`/edit_post/${postId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            var editForm = document.getElementById('edit-form-' + postId);
            if (editForm) {
                editForm.style.display = 'none';
            }

            var postContent = document.getElementById('post-content-' + postId);
            if (postContent) {
                postContent.textContent = data.content;
            }

            console.log("Reloading the page");
            location.reload();
        } else {
            console.error(`Failed to save post: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('An error occurred:', error);
    });
}