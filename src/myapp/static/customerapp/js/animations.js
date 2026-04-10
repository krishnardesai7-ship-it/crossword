document.addEventListener('DOMContentLoaded', () => {
    // Scroll Reveal Animation logic
    const revealElements = document.querySelectorAll('.block, .banner, .product');
    
    // Add reveal class to sections
    revealElements.forEach(el => {
        el.classList.add('reveal');
    });

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        const revealPoint = 150;

        revealElements.forEach(el => {
            const elTop = el.getBoundingClientRect().top;
            if (elTop < windowHeight - revealPoint) {
                el.classList.add('active');
            }
        });
    };

    window.addEventListener('scroll', revealOnScroll);
    revealOnScroll(); // Initial check

    // Add 3D Tilt effect to Banners (Optional refinement)
    const banners = document.querySelectorAll('.banner');
    banners.forEach(banner => {
        banner.addEventListener('mousemove', (e) => {
            const { left, top, width, height } = banner.getBoundingClientRect();
            const x = (e.clientX - left) / width - 0.5;
            const y = (e.clientY - top) / height - 0.5;
            
            banner.style.transform = `perspective(1000px) rotateY(${x * 10}deg) rotateX(${y * -10}deg) scale(1.02)`;
        });

        banner.addEventListener('mouseleave', () => {
            banner.style.transform = 'perspective(1000px) rotateY(0deg) rotateX(0deg) scale(1)';
        });
    });
});

// Auto-hide messages after 3 seconds
setTimeout(() => {
    const alerts = document.querySelectorAll(".message-container .alert");
    alerts.forEach(alert => {
        alert.classList.remove("show");
        setTimeout(() => alert.remove(), 500);
    });
}, 3000);

