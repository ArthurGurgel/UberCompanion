document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('sidebar-toggle');
    if (!toggle) return;

    toggle.addEventListener('click', () => {
        document.body.classList.toggle('nav-open');
    });

    // Close nav when clicking outside the sidebar menu on mobile
    document.addEventListener('click', (e) => {
        if (!document.body.classList.contains('nav-open')) return;
        const nav = document.querySelector('.nav-menu');
        if (!nav) return;
        if (!nav.contains(e.target) && !toggle.contains(e.target)) {
            document.body.classList.remove('nav-open');
        }
    });

    // Close nav on resize to desktop breakpoint (match CSS: 1024px)
    window.addEventListener('resize', () => {
        if (window.innerWidth > 1024) document.body.classList.remove('nav-open');
    });
});
