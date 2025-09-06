// 文件上传处理
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const convertBtn = document.getElementById('convertBtn');
    const uploadForm = document.getElementById('uploadForm');

    // 拖拽功能
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // 点击上传区域
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    // 文件选择
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // 处理文件
    function handleFile(file) {
        // 检查文件类型
        const allowedTypes = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.docx') && !file.name.toLowerCase().endsWith('.doc')) {
            showMessage('请选择 .docx 或 .doc 格式的文件', 'error');
            return;
        }

        // 检查文件大小 (16MB)
        if (file.size > 16 * 1024 * 1024) {
            showMessage('文件大小不能超过 16MB', 'error');
            return;
        }

        // 显示文件信息
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.style.display = 'flex';
        convertBtn.disabled = false;
        
        // 更新文件输入
        fileInput.files = new DataTransfer().files;
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
    }

    // 移除文件
    window.removeFile = function() {
        fileInfo.style.display = 'none';
        convertBtn.disabled = true;
        fileInput.value = '';
    };

    // 表单提交
    uploadForm.addEventListener('submit', function(e) {
        if (!fileInput.files.length) {
            e.preventDefault();
            showMessage('请先选择文件', 'error');
            return;
        }

        // 显示加载状态
        convertBtn.innerHTML = '<span class="loading"></span>正在转换...';
        convertBtn.disabled = true;
    });

    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 显示消息
    function showMessage(message, type = 'info') {
        // 移除现有消息
        const existingMessages = document.querySelectorAll('.flash-message');
        existingMessages.forEach(msg => msg.remove());

        // 创建新消息
        const messageDiv = document.createElement('div');
        messageDiv.className = `flash-message ${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            ${message}
        `;

        // 添加到页面
        let messagesContainer = document.querySelector('.flash-messages');
        if (!messagesContainer) {
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'flash-messages';
            document.body.appendChild(messagesContainer);
        }
        messagesContainer.appendChild(messageDiv);

        // 自动移除消息
        setTimeout(() => {
            messageDiv.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 5000);
    }

    // 添加滑出动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

// 页面加载完成后的初始化
window.addEventListener('load', function() {
    // 添加页面加载动画
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
});