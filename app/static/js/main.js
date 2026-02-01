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

    function hideGlobalLoading() {
        if (globalLoader && globalSpinner) {
            globalLoader.classList.remove('visible');
            globalSpinner.classList.remove('visible');
        }
    }

    // Hide loader when page is shown (fixes back button issue with bfcache)
    window.addEventListener('pageshow', function (event) {
        hideGlobalLoading();
    });

    function navigateWithDelay(url) {
        showGlobalLoading();
        window.location.href = url;
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

    // Mobile Navigation Toggle
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');

    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', function () {
            mobileToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        // Close menu when clicking a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileToggle.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function (e) {
            if (!mobileToggle.contains(e.target) && !navLinks.contains(e.target)) {
                mobileToggle.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }

    // Scroll-aware navbar interaction
    let lastScrollTop = 0;
    const header = document.querySelector('.site-header');
    // const headerHeight = header ? header.offsetHeight : 0; 
    // Better to use a fixed threshold or dynamic check to avoid issues if header hides

    window.addEventListener('scroll', function () {
        if (!header) return;

        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const threshold = 60; // Minimum scroll before hiding

        if (scrollTop > lastScrollTop && scrollTop > threshold) {
            // Scroll Down
            header.classList.add('hidden');
        } else {
            // Scroll Up
            header.classList.remove('hidden');
        }
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // For Mobile or negative scrolling
    }, { passive: true });

    // Theme Toggle Interaction
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
});
