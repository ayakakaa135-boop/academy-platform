/**
 * تحسينات تجربة المستخدم - JavaScript
 */

// ==========================================
// Smooth Scroll
// ==========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href !== '#!') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// ==========================================
// Navbar Scroll Effect
// ==========================================
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    // Add shadow on scroll
    if (currentScroll > 50) {
        navbar.classList.add('navbar-scrolled');
    } else {
        navbar.classList.remove('navbar-scrolled');
    }
    
    // Hide/show navbar on scroll (optional)
    if (currentScroll > lastScroll && currentScroll > 500) {
        navbar.style.transform = 'translateY(-100%)';
    } else {
        navbar.style.transform = 'translateY(0)';
    }
    
    lastScroll = currentScroll;
});

// ==========================================
// Lazy Loading Images
// ==========================================
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// ==========================================
// Animate on Scroll
// ==========================================
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    elements.forEach(el => observer.observe(el));
};

document.addEventListener('DOMContentLoaded', animateOnScroll);

// ==========================================
// Toast Notifications
// ==========================================
const showToast = (message, type = 'info') => {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getToastIcon(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
};

const createToastContainer = () => {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
};

const getToastIcon = (type) => {
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
};

// ==========================================
// Form Validation Enhancement
// ==========================================
document.querySelectorAll('form[data-validate]').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.classList.add('was-validated');
    });
});

// ==========================================
// Copy to Clipboard
// ==========================================
document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async function() {
        const text = this.dataset.copy;
        try {
            await navigator.clipboard.writeText(text);
            showToast('تم النسخ إلى الحافظة!', 'success');
        } catch (err) {
            showToast('فشل النسخ', 'danger');
        }
    });
});

// ==========================================
// Tooltips Initialization
// ==========================================
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

// ==========================================
// Popovers Initialization
// ==========================================
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

// ==========================================
// Reading Time Estimator
// ==========================================
const estimateReadingTime = (text) => {
    const wordsPerMinute = 200;
    const words = text.trim().split(/\s+/).length;
    const minutes = Math.ceil(words / wordsPerMinute);
    return minutes;
};

document.querySelectorAll('[data-reading-time]').forEach(element => {
    const text = element.textContent;
    const minutes = estimateReadingTime(text);
    const badge = document.createElement('span');
    badge.className = 'badge bg-secondary ms-2';
    badge.innerHTML = `<i class="fas fa-clock me-1"></i>${minutes} دقائق`;
    element.closest('.card-header, h1, h2, h3')?.appendChild(badge);
});

// ==========================================
// Back to Top Button
// ==========================================
const createBackToTopButton = () => {
    const button = document.createElement('button');
    button.id = 'back-to-top';
    button.className = 'btn btn-primary btn-floating';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 1000;
        display: none;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    `;
    
    document.body.appendChild(button);
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            button.style.display = 'block';
            button.classList.add('animate__animated', 'animate__fadeInUp');
        } else {
            button.style.display = 'none';
        }
    });
    
    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
};

document.addEventListener('DOMContentLoaded', createBackToTopButton);

// ==========================================
// Keyboard Shortcuts
// ==========================================
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // ESC to close modals
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});

// ==========================================
// Progress Bar for Page Loading
// ==========================================
const createProgressBar = () => {
    const bar = document.createElement('div');
    bar.id = 'page-progress';
    bar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        z-index: 9999;
        transition: width 0.3s;
        width: 0%;
    `;
    document.body.appendChild(bar);
    
    window.addEventListener('scroll', () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        bar.style.width = scrolled + '%';
    });
};

document.addEventListener('DOMContentLoaded', createProgressBar);

// ==========================================
// Auto-dismiss Alerts
// ==========================================
setTimeout(() => {
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
    });
}, 5000);

// ==========================================
// Star Rating Component
// ==========================================
document.querySelectorAll('.star-rating').forEach(container => {
    const stars = container.querySelectorAll('.star');
    const input = container.querySelector('input[type="hidden"]');
    
    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            const rating = index + 1;
            if (input) input.value = rating;
            
            stars.forEach((s, i) => {
                if (i < rating) {
                    s.classList.remove('far');
                    s.classList.add('fas');
                } else {
                    s.classList.remove('fas');
                    s.classList.add('far');
                }
            });
        });
        
        star.addEventListener('mouseenter', () => {
            stars.forEach((s, i) => {
                s.style.color = i <= index ? '#f59e0b' : '#cbd5e1';
            });
        });
    });
    
    container.addEventListener('mouseleave', () => {
        const currentRating = input ? parseInt(input.value) : 0;
        stars.forEach((s, i) => {
            s.style.color = i < currentRating ? '#f59e0b' : '#cbd5e1';
        });
    });
});

// ==========================================
// Export Functions for Global Use
// ==========================================
window.AcademyUI = {
    showToast,
    estimateReadingTime
};

console.log('🎨 تم تحميل تحسينات تجربة المستخدم بنجاح!');
