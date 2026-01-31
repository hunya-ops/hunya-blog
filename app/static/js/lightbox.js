// Lightbox 图片查看器
(function () {
    let currentIndex = 0;
    let images = [];
    let overlay = null;
    let isAnimating = false;

    // 创建 lightbox DOM
    function createLightbox() {
        overlay = document.createElement('div');
        overlay.className = 'lightbox-overlay';
        overlay.innerHTML = `
            <button class="lightbox-close">&times;</button>
            <button class="lightbox-prev">&lsaquo;</button>
            <button class="lightbox-next">&rsaquo;</button>
            <div class="lightbox-counter"></div>
            <div class="lightbox-container">
                <div class="lightbox-loader"></div>
            </div>
        `;
        document.body.appendChild(overlay);

        // 绑定事件
        overlay.querySelector('.lightbox-close').onclick = close;
        overlay.querySelector('.lightbox-prev').onclick = prev;
        overlay.querySelector('.lightbox-next').onclick = next;
        overlay.onclick = function (e) {
            if (e.target === overlay) close();
        };
    }

    // 打开 lightbox
    function open(imgList, index) {
        images = imgList;
        currentIndex = index;
        if (!overlay) createLightbox();

        // Show overlay first
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Initial load (no slide)
        // Clear container first
        const container = overlay.querySelector('.lightbox-container');
        const existingImgs = container.querySelectorAll('.lightbox-image');
        existingImgs.forEach(img => img.remove());

        // Load initial image (inside a small timeout to ensure transition context)
        setTimeout(() => {
            displayImage(index, null);
            updateControls();
        }, 50);
    }

    // 关闭 lightbox
    function close() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
        // Clear images to reset state
        setTimeout(() => {
            const container = overlay.querySelector('.lightbox-container');
            const existingImgs = container.querySelectorAll('.lightbox-image');
            existingImgs.forEach(img => img.remove());
        }, 500);
    }

    // 显示一张图片（核心逻辑）
    // direction: 'prev' (slide right), 'next' (slide left), or null (fade in)
    function displayImage(index, direction) {
        const container = overlay.querySelector('.lightbox-container');
        const loader = overlay.querySelector('.lightbox-loader');
        const newSrc = images[index];

        // 1. Create New Image
        const newImg = document.createElement('img');
        newImg.src = newSrc;
        newImg.className = 'lightbox-image';

        // Temporarily hide or set start position based on direction is tricky because we need dimensions? 
        // No, css handles centering. We just need to apply animation classes.

        // 2. Preload
        loader.style.display = 'block';

        newImg.onload = function () {
            loader.style.display = 'none';
            // Clear any inline opacity to let CSS transition work
            newImg.style.opacity = '';

            // If this is absolute start (null direction), just fade in/appear
            if (!direction) {
                container.appendChild(newImg);
                // Force reflow
                newImg.offsetWidth;
                newImg.classList.add('current');
                return;
            }

            // 3. Animation Logic
            isAnimating = true;

            // Get Current Image (Old)
            const currentImg = container.querySelector('.lightbox-image.current');

            // Add New Image to DOM
            container.appendChild(newImg);
            // Force reflow
            newImg.offsetWidth;

            // Apply classes
            if (direction === 'next') {
                newImg.classList.add('slide-in-right');
                if (currentImg) currentImg.classList.add('slide-out-left');
            } else {
                newImg.classList.add('slide-in-left');
                if (currentImg) currentImg.classList.add('slide-out-right');
            }

            // Make sure new image is marked as current after animation
            newImg.classList.add('current');
            if (currentImg) currentImg.classList.remove('current');

            // 4. Cleanup Old Image
            setTimeout(() => {
                if (currentImg) currentImg.remove();
                newImg.classList.remove('slide-in-right', 'slide-in-left'); // Remove animation classes
                isAnimating = false;
            }, 800);
        };

        // Handle error?
        newImg.onerror = function () {
            loader.style.display = 'none';
            isAnimating = false;
        };
    }

    function updateControls() {
        const counter = overlay.querySelector('.lightbox-counter');
        const prevBtn = overlay.querySelector('.lightbox-prev');
        const nextBtn = overlay.querySelector('.lightbox-next');

        if (images.length > 1) {
            counter.textContent = (currentIndex + 1) + ' / ' + images.length;
            counter.style.display = 'block';
            prevBtn.style.display = 'flex';
            nextBtn.style.display = 'flex';
        } else {
            counter.style.display = 'none';
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        }
    }

    // 上一张
    function prev(e) {
        if (e) e.stopPropagation();
        if (isAnimating) return; // Prevent spamming
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        displayImage(currentIndex, 'prev');
        updateControls();
    }

    // 下一张
    function next(e) {
        if (e) e.stopPropagation();
        if (isAnimating) return; // Prevent spamming
        currentIndex = (currentIndex + 1) % images.length;
        displayImage(currentIndex, 'next');
        updateControls();
    }

    // 键盘事件
    document.addEventListener('keydown', function (e) {
        if (!overlay || !overlay.classList.contains('active')) return;
        if (e.key === 'Escape') close();
        if (e.key === 'ArrowLeft') prev();
        if (e.key === 'ArrowRight') next();
    });

    // 绑定图片点击事件
    document.addEventListener('click', function (e) {
        const img = e.target.closest('.image-grid-display img, .post-content img');
        if (!img) return;
        if (img.parentElement.classList.contains('lightbox-container')) return; // Ignore lightbox inner images

        e.preventDefault();

        // 获取同组图片
        const container = img.closest('.image-grid-display') || img.closest('.post-content');
        const allImgs = container.querySelectorAll('img');
        const imgList = Array.from(allImgs).map(i => i.src);
        const index = imgList.indexOf(img.src);

        open(imgList, index >= 0 ? index : 0);
    });
})();
