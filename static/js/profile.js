document.addEventListener('DOMContentLoaded', () => {
    const showBtn = document.getElementById('show-password');
    const backBtn = document.getElementById('back-to-profile');
    const profileSection = document.getElementById('profile-section');
    const passwordSection = document.getElementById('password-section');

    function showPasswordForm() {
        if (profileSection) profileSection.classList.add('hidden');
        if (passwordSection) passwordSection.classList.remove('hidden');
        if (passwordSection) passwordSection.scrollIntoView({ behavior: 'smooth' });
    }

    function showProfileForm() {
        if (passwordSection) passwordSection.classList.add('hidden');
        if (profileSection) profileSection.classList.remove('hidden');
        if (profileSection) profileSection.scrollIntoView({ behavior: 'smooth' });
    }

    if (showBtn) showBtn.addEventListener('click', showPasswordForm);
    if (backBtn) backBtn.addEventListener('click', showProfileForm);
});
