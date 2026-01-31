document.addEventListener('DOMContentLoaded', function () {
    // Image lazy load skeleton
    const images = document.querySelectorAll('.post-content img, .image-grid-display img');

    images.forEach(img => {
        if (img.closest('.lightbox-container') || img.parentElement.classList.contains('image-placeholder')) return;

        const wrapper = document.createElement('span');
        wrapper.className = 'image-placeholder';
        img.parentNode.insertBefore(wrapper, img);
        wrapper.appendChild(img);

        if (img.complete) {
            wrapper.classList.add('loaded');
        } else {
            img.onload = function () {
                wrapper.classList.add('loaded');
            };
            img.onerror = function () {
                wrapper.classList.add('error');
            }
        }
    });

    // Global page transition loader
    const globalLoader = document.getElementById('globalLoader');
    const globalSpinner = document.getElementById('globalSpinner');

    function showGlobalLoading() {
        if (globalLoader && globalSpinner) {
            globalLoader.classList.add('visible');
            globalSpinner.classList.add('visible');
        }
    }

    function navigateWithDelay(url) {
        showGlobalLoading();
        setTimeout(() => {
            window.location.href = url;
        }, 500);
    }

    // Add loading animation to nav links (except current active)
    document.querySelectorAll('.site-header nav ul a').forEach(link => {
        link.addEventListener('click', function (e) {
            // Don't navigate if clicking current page
            if (this.classList.contains('active')) {
                e.preventDefault();
                return;
            }
            e.preventDefault();
            navigateWithDelay(this.href);
        });
    });

    // Add loading animation to pagination links
    document.querySelectorAll('.pagination a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            navigateWithDelay(this.href);
        });
    });
});
