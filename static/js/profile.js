document.addEventListener('DOMContentLoaded', function(){
    const showPwd = document.getElementById('show-password');
    const backBtn = document.getElementById('back-to-profile');
    const profileSection = document.getElementById('profile-section');
    const passwordSection = document.getElementById('password-section');

    function toggleToPassword() {
        if (profileSection) profileSection.classList.add('hidden');
        if (passwordSection) passwordSection.classList.remove('hidden');
        // focus first input
        const first = passwordSection.querySelector('input');
        if (first) first.focus();
    }

    function toggleToProfile() {
        if (passwordSection) passwordSection.classList.add('hidden');
        if (profileSection) profileSection.classList.remove('hidden');
        const first = profileSection.querySelector('input');
        if (first) first.focus();
    }

    if (showPwd) showPwd.addEventListener('click', toggleToPassword);
    if (backBtn) backBtn.addEventListener('click', toggleToProfile);
});
