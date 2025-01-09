// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            if (entry.target.classList.contains('card')) {
                entry.target.style.transitionDelay = '0.2s';
            }
        }
    });
}, observerOptions);

// Observe all sections and cards
document.querySelectorAll('.section, .card').forEach(el => {
    el.classList.add('fade-in');
    observer.observe(el);
});

// Parallax effect for developer info section
window.addEventListener('scroll', () => {
    const developerInfo = document.querySelector('.developer-info');
    const scrolled = window.pageYOffset;
    developerInfo.style.backgroundPositionY = scrolled * 0.5 + 'px';
});

// Dynamic navbar background
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
    if (window.scrollY > 100) {
        nav.classList.add('nav-scrolled');
    } else {
        nav.classList.remove('nav-scrolled');
    }
});

// Typing effect for developer info
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.innerHTML = '';
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Initialize typing effect
document.addEventListener('DOMContentLoaded', () => {
    const developerTitle = document.querySelector('.developer-info h2');
    const originalText = developerTitle.innerText;
    typeWriter(developerTitle, originalText);
});

// Interactive cards
document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'none';
    });
});

// Theme toggle
let isDarkMode = false;
function toggleTheme() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode');
    
    const themeToggle = document.querySelector('.theme-toggle');
    themeToggle.innerHTML = isDarkMode ? '☀️' : '🌙';
    
    localStorage.setItem('darkMode', isDarkMode);
}

// Initialize theme from localStorage
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'true') {
        toggleTheme();
    }
});
