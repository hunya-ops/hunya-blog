// 多图上传处理与交互增强
const MAX_IMAGES = 9;
const imageGrid = document.getElementById('image-grid');
const addBtn = document.getElementById('add-image-btn');
const imageInput = document.getElementById('image-input');
const imageUrlsInput = document.getElementById('image-urls');
const uploadArea = document.getElementById('upload-area');

let images = [];

// 初始化已有图片
if (imageUrlsInput && imageUrlsInput.value) {
    images = imageUrlsInput.value.split(',').filter(url => url.trim());
    renderImages();
}

// 点击添加按钮
if (addBtn) {
    addBtn.addEventListener('click', () => {
        if (images.length < MAX_IMAGES) {
            imageInput.click();
        }
    });
}

// 文件选择
if (imageInput) {
    imageInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
        imageInput.value = '';
    });
}

// 拖拽上传支持
if (uploadArea) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('highlight');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('highlight');
        }, false);
    });

    uploadArea.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = Array.from(dt.files);
        handleFiles(files);
    }, false);
}

function handleFiles(files) {
    const remaining = MAX_IMAGES - images.length;
    const toUpload = files.filter(f => f.type.startsWith('image/')).slice(0, remaining);
    toUpload.forEach(file => uploadImage(file));
}

// 粘贴图片覆盖全局
document.addEventListener('paste', (e) => {
    // 仅在动态编辑器中或特定区域粘贴时处理
    if (!uploadArea) return;

    const items = e.clipboardData?.items;
    if (!items || images.length >= MAX_IMAGES) return;

    for (let item of items) {
        if (item.type.startsWith('image/')) {
            const file = item.getAsFile();
            if (file) uploadImage(file);
        }
    }
});

// 上传图片
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    // 显示上传中状态 (使用一个临时对象)
    const tempId = 'loading-' + Date.now() + Math.random();
    images.push({ id: tempId, loading: true });
    renderImages();

    try {
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        const response = await fetch('/api/upload', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });
        const data = await response.json();

        // 查找并替换临时项
        const index = images.findIndex(img => img.id === tempId);

        if (data.success) {
            if (index !== -1) images[index] = data.url;
            else images.push(data.url);
            updateInput();
            renderImages();
        } else {
            if (index !== -1) images.splice(index, 1);
            alert(data.error || '上传失败');
            renderImages();
        }
    } catch (err) {
        const index = images.findIndex(img => img.id === tempId);
        if (index !== -1) images.splice(index, 1);
        alert('上传失败: ' + err.message);
        renderImages();
    }
}

// 删除图片 (全局可用)
window.removeImage = function (index) {
    images.splice(index, 1);
    updateInput();
    renderImages();
};

// 放大查看图片 (简单实现)
window.previewImage = function (url) {
    const viewer = document.createElement('div');
    viewer.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.9); z-index: 9999;
        display: flex; align-items: center; justify-content: center;
        cursor: zoom-out; backdrop-filter: blur(10px);
    `;
    const img = document.createElement('img');
    img.src = url;
    img.style.cssText = 'max-width: 90%; max-height: 90%; border-radius: 8px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);';
    viewer.appendChild(img);
    viewer.onclick = () => viewer.remove();
    document.body.appendChild(viewer);
};

// 更新隐藏输入框
function updateInput() {
    if (imageUrlsInput) {
        imageUrlsInput.value = images.filter(img => typeof img === 'string').join(',');
    }
}

// 渲染图片网格
function renderImages() {
    if (!imageGrid) return;
    imageGrid.innerHTML = '';

    images.forEach((img, index) => {
        const item = document.createElement('div');
        item.className = 'image-item';

        if (img.loading) {
            item.innerHTML = '<div class="loading-spinner"></div>';
        } else {
            item.innerHTML = `
                <img src="${img}" alt="" onclick="previewImage('${img}')" style="cursor: pointer;">
                <button type="button" class="remove-btn" onclick="event.stopPropagation(); removeImage(${index})">×</button>
            `;
        }
        imageGrid.appendChild(item);
    });

    // 重新排序或确保添加按钮始终在最后
    if (images.length < MAX_IMAGES) {
        imageGrid.appendChild(addBtn);
        addBtn.style.display = 'flex';
    } else {
        addBtn.style.display = 'none';
    }
}
